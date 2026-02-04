Phase 1: Project Scaffolding & Docker Foundation
   * I will create the project directory structure as specified in the PDF.
   * I will set up the docker-compose.yml file to manage the required services: a
     FastAPI backend, a PostgreSQL database with pgvector for vector similarity search,
     and the n8n automation tool.
   * I will create an .env.example file to list all the necessary environment variables
     for configuration.


  Phase 2: Backend Core & Authentication
   * I will define the database schema in the backend using SQLAlchemy models,
     including tables for students, assignments, analysis results, and academic
     sources. I will set up database migrations to create these tables.
   * I will implement JWT-based authentication with /register and /login endpoints.
     Initially, this will use hardcoded user data as allowed.
   * I will create the basic structure for all the API endpoints (/upload,
     /analysis/{id}, /sources) and secure them.


  Phase 3: RAG Implementation (Core AI Feature)
   * I will create a script to load the sample academic papers, generate text
     embeddings using the OpenAI API, and store them in our PostgreSQL/pgvector
     database. This will form the knowledge base for our RAG system.
   * I will build a rag_service in the backend that can take a piece of text, find
     relevant academic sources from the database, and return them. This will power the
     /sources endpoint.


  Phase 4: n8n Workflow & Full Integration
   * I will design the n8n workflow, starting with a webhook to receive assignments
     from the backend.
   * The workflow will perform the key processing steps:
       1. Extract text from the uploaded assignment file (e.g., PDF, DOCX).
       2. Use the RAG service to find relevant sources.
       3. Call an LLM (like OpenAI) to perform the analysis: identify topics, suggest
          research questions, and detect potential plagiarism by comparing the
          assignment to the retrieved sources.
       4. Store the structured results in the PostgreSQL database.
   * I will fully implement the /upload endpoint in the backend to trigger this n8n
     workflow and the /analysis/{id} endpoint to retrieve the results.


  Phase 5: Finalization, Documentation & Delivery
   * I will write a comprehensive README.md with detailed setup and usage instructions.
   * I will prepare the required technical documentation explaining the RAG
     architecture, prompting strategies, and database design.
   * I will ensure all components are working together smoothly and the project is
     ready for delivery as per the requirements.