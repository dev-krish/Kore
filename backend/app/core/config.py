import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KORE"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"

    # Database
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "kore_db")

    # Security
    SECRET_KEY: str = os.getenv("NEXTAUTH_SECRET", "kore_super_secret_jwt_key_change_in_production_min_32_chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # AI Engine
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")  # ollama | openai | mock
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:4b")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Search Provider
    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "demo")  # demo | serpapi | tavily | brave
    SEARCH_API_KEY: Optional[str] = os.getenv("SEARCH_API_KEY", None)

    # Gmail OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/integrations/gmail/callback")

    # URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # Agent Limits
    MAX_EXECUTION_STEPS: int = 15
    MAX_TOOL_RETRIES: int = 2
    TOOL_TIMEOUT_SECONDS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
