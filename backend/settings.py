from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    JWT_SECRET_KEY: str
    OPENAI_API_KEY: str
    INTERNAL_API_KEY: str
    N8N_WEBHOOK_URL: str | None = None
    GEMINI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
