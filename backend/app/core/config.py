import os
import secrets
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "KORE"
    VERSION: str = "0.2.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")  # development | production | test
    ALLOW_DEMO_AUTH: bool = os.getenv("ALLOW_DEMO_AUTH", "true").lower() in ("true", "1", "yes")

    # Database
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "kore_db")

    # Security
    # In development a default is permitted; in production a secure key >= 32 chars is strictly required
    SECRET_KEY: str = os.getenv("NEXTAUTH_SECRET", "kore_dev_secret_key_min_32_characters_long_for_security_123")
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
    GMAIL_MODE: str = os.getenv("GMAIL_MODE", "live")  # live | demo

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

    def validate_production_security(self):
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or self.SECRET_KEY.startswith("kore_dev_") or len(self.SECRET_KEY) < 32:
                raise ValueError("CRITICAL SECURITY ERROR: Production deployment requires a secure, non-default SECRET_KEY with at least 32 characters.")

settings = Settings()
settings.validate_production_security()
