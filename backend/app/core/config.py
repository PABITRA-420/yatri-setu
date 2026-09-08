import os
from typing import List, Optional

class Settings:
    PROJECT_NAME: str = "Yatri Setu API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DESCRIPTION: str = "Hyperlocal and rural tourism platform with active crowd control and traveler safety (Smart India Hackathon 2026)"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"
    ]
    
    # Database settings (Defaults to local SQLite for frictionless dev/tests, PostgreSQL in production)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./yatri_setu.db")

    # Weather Provider Settings
    WEATHER_PROVIDER: str = os.getenv("WEATHER_PROVIDER", "mock")
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY", None)

    # AI Provider Settings (SIH 2026: mock default ensures zero-API-key seamless demo)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

settings = Settings()
