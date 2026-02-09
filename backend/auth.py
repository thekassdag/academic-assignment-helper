from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import bcrypt
import logging

from models import Student, StudentCreate, StudentLogin, Token
from settings import settings
from database import get_db

# --- initialization ---
auth_router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("uvicorn.error")

# --- constants ---
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
AUTH_HEADER = APIKeyHeader(
    name="Authorization",
    scheme_name="Bearer",
    description="past: 'Bearer [AccessToken]'",
    auto_error=False,
)



# --- route dependents ---
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM
    )
    return encoded_jwt


def get_token(auth: str = Depends(AUTH_HEADER)):
    if not auth:
        raise HTTPException(
            status_code=401, detail="Missing Authorization header"
        )

    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    return auth.split(" ", 1)[1]


def get_current_user(
    token: str = Depends(get_token), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(Student).filter(Student.email == email).first()
    if user is None:
        raise credentials_exception
    return user


# -- routes ---
@auth_router.post("/register", response_model=Token)
def register(student: StudentCreate, db: Session = Depends(get_db)):
    # check if user with same email or student ID already exists
    existing_user = (
        db.query(Student)
        .filter(
            (Student.email == student.email)
            | (Student.student_id == student.student_id)
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email or student ID already exists",
        )

    # hashing the password
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(
        student.password.encode("utf-8"), salt
    ).decode("utf-8")

    db_student = Student(
        email=student.email,
        password_hash=hashed_password,  # store the hash as text not bytes that way we decoded to utf-8
        full_name=student.full_name,
        student_id=student.student_id,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_student.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/login", response_model=Token)
def login(
    login_data: StudentLogin,
    db: Session = Depends(get_db),
):
    logger.info(f"Login data: {login_data}")

    student = (
        db.query(Student).filter(Student.email == login_data.email).first()
    )
    logger.info(f"Student: {student}")
    if not student:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    is_password_correct = bcrypt.checkpw(
        login_data.password.encode("utf-8"),
        student.password_hash.encode("utf-8"),
    )
    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": student.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
