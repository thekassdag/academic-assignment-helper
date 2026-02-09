import json
import os
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from google import genai
from pgvector.sqlalchemy import Vector
from pgvector.psycopg2 import register_vector

from settings import settings
from models import Base, AcademicSource

# Database setup
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Gemini client setup
client = genai.Client(api_key=settings.GEMINI_API_KEY)

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

def ingest_academic_sources(json_file_path: str):
    db = SessionLocal()
    try:
        with open(json_file_path, 'r') as f:
            sources_data = json.load(f)

        for source_data in sources_data:
            full_text = source_data.get("full_text", "")
            if not full_text:
                print(f"Skipping source due to missing full_text: {source_data.get('title', 'N/A')}")
                continue

            embedding = get_embedding(full_text)
            
            academic_source = AcademicSource(
                title=source_data.get("title"),
                authors=source_data.get("authors"),
                publication_year=source_data.get("publication_year"),
                abstract=source_data.get("abstract"),
                full_text=full_text,
                source_type=source_data.get("source_type"),
                embedding=embedding
            )
            db.add(academic_source)
        
        db.commit()
        print(f"Successfully ingested {len(sources_data)} academic sources.")
    except Exception as e:
        db.rollback()
        print(f"Error during ingestion: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure the vector extension is enabled
    conn = engine.connect()
    conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()
    conn.close()

    # Register pgvector type with psycopg2
    # register_vector(engine.raw_connection().connection)

    json_file = "/app/data/sample_academic_sources.json" # Path inside the container
    ingest_academic_sources(json_file)
