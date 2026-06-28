from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "changeme"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "homoeo_cdss"
    POSTGRES_USER: str = "homoeo_admin"
    POSTGRES_PASSWORD: str = "password"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_MATERIA_MEDICA: str = "materia_medica"
    QDRANT_COLLECTION_CLINIC_CASES: str = "clinic_cases"
    QDRANT_COLLECTION_DOCTOR_NOTES: str = "doctor_notes"
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-sonnet-4-6"
    LLM_MAX_TOKENS: int = 2048
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    WHISPER_MODEL: str = "medium"
    WHATSAPP_API_URL: str = ""
    WHATSAPP_PHONE_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    DATA_RETENTION_DAYS: int = 2555
    CONSENT_VERSION: str = "1.0"

    class Config:
        env_file = ".env"

settings = Settings()
