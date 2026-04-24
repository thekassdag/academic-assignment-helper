from sqlalchemy.orm import Session
from google import genai

from models import AcademicSource
from settings import settings

# Gemini client setup
client = genai.Client(api_key=settings.GEMINI_API_KEY)  # set your Gemini API key in settings

from google.genai import types

...

def get_embedding(text: str, model: str = "gemini-embedding-001", dimension: int = 1536):
    """
    Generates an embedding for the given text using Google Gemini API.
    
    Args:
        text: The text to embed.
        model: The Gemini embedding model to use.
        dimension: Output dimension (e.g., 1536 to match DB column).
        
    Returns:
        A list of floats representing the embedding vector.
    """
    text = text.replace("\n", " ")
    result = client.models.embed_content(
        model=model,
        contents=[text],
        config=types.EmbedContentConfig(output_dimensionality=dimension)
    )
    return result.embeddings[0].values

def find_relevant_sources(query_text: str, db: Session, top_k: int = 5):
    """
    Finds relevant academic sources from the database using vector similarity search.

    Args:
        query_text: The text to search for (e.g., assignment topic).
        db: The database session.
        top_k: The number of top results to return.

    Returns:
        A list of AcademicSource objects.
    """
    query_embedding = get_embedding(query_text)

    # Use pgvector l2_distance operator to find nearest neighbors
    relevant_sources = (
        db.query(AcademicSource)
        .order_by(AcademicSource.embedding.l2_distance(query_embedding))
        .limit(top_k)
        .all()
    )
    
    return relevant_sources