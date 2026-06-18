from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root: backend/app/core -> ../../../
PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+asyncpg://traceos:traceos_secret@localhost:5432/traceos"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "change-me-in-production-use-strong-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7
    CORS_ORIGINS: str = "http://localhost:3000"
    EMBEDDING_DIMENSION: int = 1536

    # OpenRouter — set OPENROUTER_API_KEY in the project root .env file
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_APP_NAME: str = "TraceOS"
    OPENROUTER_APP_URL: str = "http://localhost:3000"
    LLM_MODEL: str = "openai/gpt-4o-mini"
    EMBEDDING_MODEL: str = "openai/text-embedding-3-small"


settings = Settings()
