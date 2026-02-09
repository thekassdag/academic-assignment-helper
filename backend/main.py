from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
    APIRouter,
    Security,
    BackgroundTasks,
)
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session, joinedload
from typing import List
import aiohttp
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from auth import auth_router, get_current_user
from models import (
    Student,
    AcademicSourceResponse,
    Assignment,
    AnalysisResultResponse,
    N8nAnalysisResultCreate,
    AnalysisResult,
    AcademicSource
)
from database import get_db
from rag_service import find_relevant_sources, get_embedding
from settings import settings

# --- initialization ---
app = FastAPI()

# --- Constants ---
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]
MAX_FILE_SIZE_MB = 5  # in mbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # in bites
INTERNAL_API_KEY_HEADER = APIKeyHeader(
    name="X-API-Key", scheme_name="Internal API Key", auto_error=True
)

# --- helpers ---
async def send_to_n8n(assignment_id: int, email: str, file: UploadFile):
    # Move the file pointer to the beginning just in case
    file.file.seek(0)
    
    # read files in-memory
    file_bytes = await file.read()


    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field(
            "data",
            file_bytes,
            filename=file.filename,
            content_type=file.content_type,
        )

        headers = {
            # "Content-Type": "multipart/form-data",
            "X-API-Key": settings.INTERNAL_API_KEY,
        }

        async with session.post(
            f'{settings.N8N_WEBHOOK_URL}?id={assignment_id}&email={email}', data=data, headers=headers
        ) as response:
            response.raise_for_status()


# --- router dependents ---
async def get_internal_api_key(
    api_key_header: str = Security(INTERNAL_API_KEY_HEADER),
):
    """
    IN order to comminucate with our intenral servies we need interanl api key
    """
    if api_key_header == settings.INTERNAL_API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


# --- Routers ---

internal_router = APIRouter(
    prefix="/internal",
    tags=["internal"],
    dependencies=[Depends(get_internal_api_key)],
)


@internal_router.post("/analysis-results")
def create_analysis_result(
    result_data: N8nAnalysisResultCreate, db: Session = Depends(get_db)
):
    """
    Internal endpoint for n8n to post analysis results.
    """
    db_assignment = (
        db.query(Assignment)
        .filter(Assignment.id == result_data.assignment_id)
        .first()
    )
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Update Assignment table
    db_assignment.original_text = result_data.original_text
    db_assignment.topic = result_data.topic
    db_assignment.academic_level = result_data.academic_level
    db_assignment.word_count = result_data.word_count

    # Create AnalysisResult record
    db_analysis_result = AnalysisResult(
        assignment_id=result_data.assignment_id,
        suggested_sources=result_data.suggested_sources,
        plagiarism_score=result_data.plagiarism_score,
        research_suggestions=result_data.research_suggestions,
        citation_recommendations=result_data.citation_recommendations,
        confidence_score=result_data.confidence_score,
    )

    db.add(db_analysis_result)
    db.commit()
    db.refresh(db_analysis_result)

    return {"message": "Analysis result created successfully"}


@internal_router.get("/sources", response_model=List[AcademicSourceResponse])
async def get_academic_sources(
    q: str,
    db: Session = Depends(get_db),
):
    """
    Searches for academic sources relevant to the query string 'q' and returns them with a similarity score.
    """
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' cannot be empty.",
        )

    # Get relevant sources from the database (ordered by similarity)
    relevant_sources_db = find_relevant_sources(query_text=q, db=db)

    # Calculate query embedding
    query_embedding = np.array(get_embedding(q)).reshape(1, -1)

    # Prepare response with similarity scores
    response_sources = []
    for source in relevant_sources_db:
        source_embedding = np.array(source.embedding).reshape(1, -1)
        similarity = cosine_similarity(query_embedding, source_embedding)[0][0]
        
        response_sources.append(AcademicSourceResponse(
            id=source.id,
            title=source.title,
            authors=source.authors,
            publication_year=source.publication_year,
            abstract=source.abstract,
            source_type=source.source_type,
            similarity_score=float(similarity)
        ))
    
    return response_sources




# include routes 
app.include_router(auth_router)
app.include_router(internal_router)

# reaming routes
@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/upload")
async def upload_assignment(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
    file: UploadFile = File(...),
):
    """
    Accepts an assignment file, stores it, creates a database record,
    and triggers the n8n analysis workflow.
    """
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only PDF and DOCX allowed.",
        )

    # Check file size
    file.file.seek(0, 2)  # move to end of file
    file_size = file.file.tell()
    file.file.seek(0)  # reset pointer to start
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB} MB.",
        )

    # Create assignment record in the database
    db_assignment = Assignment(
        student_id=current_user.id, filename=file.filename
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)

    # Add background job
    background_tasks.add_task(
        send_to_n8n, db_assignment.id, current_user.email, file
    )

    return {"assignment_id": db_assignment.id}


@app.get("/analysis/{assignment_id}", response_model=AnalysisResultResponse)
async def get_analysis_results(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: Student = Depends(get_current_user),
):
    """
    Retrieves the analysis results for a specific assignment.
    """
    assignment = (
        db.query(Assignment)
        .options(joinedload(Assignment.analysis_results))
        .filter(
            Assignment.id == assignment_id,
            Assignment.student_id == current_user.id,
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found.",
        )

    if assignment.analysis_results:
        return AnalysisResultResponse(
            id=assignment.id,
            filename=assignment.filename,
            uploaded_at=assignment.uploaded_at,
            status="Completed",
            analysis=assignment.analysis_results,
        )
    else:
        return AnalysisResultResponse(
            id=assignment.id,
            filename=assignment.filename,
            uploaded_at=assignment.uploaded_at,
            status="Pending",
            analysis=None,
        )
