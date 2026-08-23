"""
AeroGuard Backend Configuration
-------------------------------
Manages application settings, CORS policies, environment variables, and API prefix.
"""

import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "AeroGuard"
    PROJECT_TITLE: str = "AeroGuard — AI + IoT Platform for Predicting and Preventing Pollution Risks"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/aeroguard"
    )
    
    CORS_ORIGINS: List[str] = [
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,*"
        ).split(",") if origin.strip()
    ]

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "allow"
    }


settings = Settings()
