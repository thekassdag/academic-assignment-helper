from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, FLOAT, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(Text)
    student_id = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    assignments = relationship("Assignment", back_populates="student")

class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    filename = Column(Text)
    original_text = Column(Text)
    topic = Column(Text)
    academic_level = Column(Text)
    word_count = Column(Integer)
    uploaded_at = Column(TIMESTAMP, server_default=func.now())

    student = relationship("Student", back_populates="assignments")
    analysis_results = relationship("AnalysisResult", back_populates="assignment", uselist=False)

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False)
    suggested_sources = Column(JSON)
    plagiarism_score = Column(FLOAT)
    research_suggestions = Column(Text)
    citation_recommendations = Column(Text)
    confidence_score = Column(FLOAT)
    analyzed_at = Column(TIMESTAMP, server_default=func.now())

    assignment = relationship("Assignment", back_populates="analysis_results")

class AcademicSource(Base):
    __tablename__ = 'academic_sources'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text)
    authors = Column(Text)
    publication_year = Column(Integer)
    abstract = Column(Text)
    full_text = Column(Text)
    source_type = Column(Text)  # 'paper', 'textbook', 'course_material'
    embedding = Column(Vector(1536))

# Pydantic models for API
class StudentCreate(BaseModel):
    email: str
    password: str
    full_name: str
    student_id: str

class StudentLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class AcademicSourceResponse(BaseModel):
    id: int
    title: str | None
    authors: str | None
    publication_year: int | None
    abstract: str | None
    source_type: str | None
    similarity_score: float | None

    class Config:
        from_attributes = True

class AnalysisResultModel(BaseModel):
    suggested_sources: Optional[List[dict]] = None
    plagiarism_score: Optional[float] = None
    research_suggestions: Optional[str] = None
    citation_recommendations: Optional[str] = None
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AnalysisResultResponse(BaseModel):
    id: int
    filename: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    status: str
    analysis: Optional[AnalysisResultModel] = None

    class Config:
        from_attributes = True


class N8nAnalysisResultCreate(BaseModel):
    assignment_id: int
    suggested_sources: List[dict]
    plagiarism_score: float
    research_suggestions: str
    citation_recommendations: str
    confidence_score: float
    original_text: str
    topic: str
    academic_level: str
    word_count: int
