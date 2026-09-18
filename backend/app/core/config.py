import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv


# Load backend/.env for local development while preserving values supplied by
# Render, Docker, or another deployment environment.
_BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(_BACKEND_DIR / ".env", override=False)

class Settings:
    PROJECT_NAME: str = "Yatri Setu API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DESCRIPTION: str = "Hyperlocal and rural tourism platform with active crowd control and traveler safety (Smart India Hackathon 2026)"
    
    # Environment (development | staging | production)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # CORS Configuration: comma-separated origins or safe defaults (no wildcard in production)
    @property
    def CORS_ORIGINS(self) -> List[str]:
        raw_origins = os.getenv("CORS_ORIGINS")
        defaults = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "https://yatri-setu.vercel.app",
            "https://yatri-setu.onrender.com",
            "https://yatri-setu-api.onrender.com"
        ]
        if raw_origins:
            parsed = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]
            return list(dict.fromkeys(parsed + defaults))
        return defaults
    
    # Database settings (PostgreSQL in production, SQLite fallback in local/tests)
    @property
    def DATABASE_URL(self) -> str:
        raw_url = os.getenv("DATABASE_URL", "sqlite:///./yatri_setu.db")
        # Normalize SQLAlchemy 2.0 URL prefix if provider outputs postgres://
        if raw_url.startswith("postgres://"):
            return raw_url.replace("postgres://", "postgresql://", 1)
        return raw_url

    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "15"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))

    # Weather Provider Settings (demo | openweather | unavailable)
    WEATHER_PROVIDER: str = os.getenv("WEATHER_PROVIDER", "openweather")
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY", None)
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY", os.getenv("OPENWEATHER_API_KEY", None))

    # Traffic Provider Settings (demo | tomtom | google | unavailable)
    TRAFFIC_PROVIDER: str = os.getenv("TRAFFIC_PROVIDER", "tomtom")
    TRAFFIC_API_KEY: Optional[str] = os.getenv("TRAFFIC_API_KEY", None)
    TOMTOM_API_KEY: Optional[str] = os.getenv("TOMTOM_API_KEY", os.getenv("TRAFFIC_API_KEY", None))

    # Road Routing Provider Settings (demo | osrm | fallback)
    ROUTING_PROVIDER: str = os.getenv("ROUTING_PROVIDER", "osrm")

    # Dynamic Pressure Refresh Settings
    PRESSURE_REFRESH_INTERVAL_SECONDS: int = int(os.getenv("PRESSURE_REFRESH_INTERVAL_SECONDS", "300"))

    # AI Provider Settings (Gemini primary, Groq fallback, Mock final fallback)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    AI_FALLBACK_PROVIDER: str = os.getenv("AI_FALLBACK_PROVIDER", "groq")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # Legacy / Alternative AI Settings (preserved for backward compatibility)
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Map Provider Settings (Internal curated routes by default; no external key required)
    MAPS_API_KEY: Optional[str] = os.getenv("MAPS_API_KEY", None)

    # Optional Administrative API Authorization Key
    ADMIN_SECRET_KEY: Optional[str] = os.getenv("ADMIN_SECRET_KEY", None)

    # Rate Limiting Settings (requests per minute)
    RATE_LIMIT_AI_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_AI_PER_MINUTE", "60"))
    RATE_LIMIT_SOS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_SOS_PER_MINUTE", "120"))
    RATE_LIMIT_GENERAL_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_GENERAL_PER_MINUTE", "300"))

    # Capacity-Aware Flow Management Settings (Milestone 7D)
    REDIRECTION_ACCEPTANCE_RATE: float = float(os.getenv("REDIRECTION_ACCEPTANCE_RATE", "0.15"))

settings = Settings()


