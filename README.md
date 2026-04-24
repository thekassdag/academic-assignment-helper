# Academic Assignment Helper & Plagiarism Detector (RAG-Powered)

<img width="1629" height="580" alt="Screenshot from 2026-02-09 10-11-52" src="https://github.com/user-attachments/assets/7f5d2467-f5f9-4e2d-8e0a-aa2e02bfc395" />
<img width="1456" height="531" alt="Screenshot from 2026-02-09 10-10-17" src="https://github.com/user-attachments/assets/8994b1c1-c124-4387-9872-28493a63d7c4" />


This project is a comprehensive backend system designed to assist with academic assignments by providing research source suggestions and plagiarism detection. It is powered by a Retrieval-Augmented Generation (RAG) pipeline and orchestrated using Docker.

## Features

- **JWT-based Authentication**: Secure endpoints for user registration and login.
- **Assignment Upload**: Users can upload their assignments for analysis.
- **RAG-Powered Source Suggestions**: Utilizes a vector database (PostgreSQL with pgvector) to find relevant academic sources for a given topic.
- **Plagiarism Detection**: (Handled by n8n) Compares assignment text against a database of academic papers.
- **Automated Workflow**: Integrated with n8n to process assignments, perform analysis, and store results.
- **Dockerized Services**: All services (FastAPI Backend, PostgreSQL, n8n, pgAdmin) are containerized for easy setup and deployment.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector extension
- **Authentication**: JWT (JSON Web Tokens)
- **Vector Embeddings**: OpenAI API (`text-embedding-ada-002`)
- **Workflow Automation**: n8n
- **Containerization**: Docker & Docker Compose

## Setup and Installation

### Prerequisites

- Docker
- Docker Compose

### 1. Clone the Repository

```bash
git clone <repository-url>
cd academic-assignment-helper
```

### 2. Configure Environment Variables

Create a `.env` file by copying the example file:

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in the required values:

- `OPENAI_API_KEY`: Your API key from OpenAI.
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: Your desired PostgreSQL credentials. These must match the values in `docker-compose.yml`.
- `JWT_SECRET_KEY`: A strong, secret key for encoding JWTs. You can generate one using `openssl rand -hex 32`.
- `N8N_WEBHOOK_URL`: The full URL for the n8n webhook that the backend will trigger. It should point to the n8n service (e.g., `http://localhost:5678/webhook/assignment-analysis`).

### 3. Build and Run Services

Start all the services using Docker Compose:

```bash
docker-compose up --build -d
```

This will start the FastAPI backend, PostgreSQL database, n8n, and pgAdmin.

### 4. Run Database Migrations

Once the containers are running, execute the database migrations to create the necessary tables.

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Ingest Academic Data

Populate the vector database with the sample academic sources. This script will generate embeddings for the data and store them.

```bash
docker-compose exec backend python ingest_data.py
```

The backend is now fully set up and ready to receive requests.

## API Endpoints

The API is accessible at `http://localhost:8000`.

### Authentication

#### `POST /auth/register`

Register a new student account.

- **Body**:
  ```json
  {
    "email": "student@example.com",
    "password": "a-strong-password",
    "full_name": "John Doe",
    "student_id": "S12345"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "your-jwt-token",
    "token_type": "bearer"
  }
  ```

#### `POST /auth/login`

Log in to get an access token. The endpoint uses a form data payload.

- **Body** (`application/x-www-form-urlencoded`):
  - `username`: The student's email.
  - `password`: The student's password.
- **Response**:
  ```json
  {
    "access_token": "your-jwt-token",
    "token_type": "bearer"
  }
  ```

### Main API (Requires Authentication)

*You must include `Authorization: Bearer <your-jwt-token>` in the headers for all of these endpoints.*

#### `POST /upload`

Upload an assignment file for analysis.

- **Body** (`multipart/form-data`):
  - `file`: The assignment file (e.g., a `.pdf` or `.docx`).
- **Response**:
  ```json
  {
    "assignment_id": 1
  }
  ```

#### `GET /analysis/{assignment_id}`

Retrieve the analysis results for a previously uploaded assignment.

- **Path Parameter**:
  - `assignment_id`: The ID returned from the `/upload` endpoint.
- **Response** (if analysis is complete):
  ```json
  {
    "id": 1,
    "filename": "my_assignment.pdf",
    "uploaded_at": "2026-02-05T12:00:00Z",
    "status": "Completed",
    "analysis": {
      "suggested_sources": [...],
      "plagiarism_score": 0.15,
      "flagged_sections": [...],
      "research_suggestions": "...",
      "citation_recommendations": "...",
      "analyzed_at": "2026-02-05T12:05:00Z"
    }
  }
  ```
- **Response** (if analysis is pending):
  ```json
  {
    "id": 1,
    "filename": "my_assignment.pdf",
    "uploaded_at": "2026-02-05T12:00:00Z",
    "status": "Pending",
    "analysis": null
  }
  ```

#### `GET /sources`

Search for relevant academic sources from the vector database.

- **Query Parameter**:
  - `q`: The search query or topic (e.g., `q=The history of machine learning`).
- **Response**:
  ```json
  [
    {
      "id": 123,
      "title": "A Comprehensive Study on Neural Networks",
      "authors": "Jane Smith, et al.",
      "publication_year": 2022,
      "abstract": "...",
      "source_type": "paper"
    }
  ]
  ```
