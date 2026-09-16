import os
from typing import List, Optional

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
        if raw_origins:
            return [orig.strip() for orig in raw_origins.split(",") if orig.strip()]
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000"
        ]
    
    # Database settings (PostgreSQL in production, SQLite fallback in local/tests)
    @property
    def DATABASE_URL(self) -> str:
        raw_url = os.getenv("DATABASE_URL", "sqlite:///./yatri_setu.db")
        # Normalize SQLAlchemy 2.0 URL prefix if provider outputs postgres://
        if raw_url.startswith("postgres://"):
            return raw_url.replace("postgres://", "postgresql://", 1)
        return raw_url

    # Weather Provider Settings (demo | openweather | unavailable)
    WEATHER_PROVIDER: str = os.getenv("WEATHER_PROVIDER", "demo")
    OPENWEATHER_API_KEY: Optional[str] = os.getenv("OPENWEATHER_API_KEY", None)
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY", os.getenv("OPENWEATHER_API_KEY", None))

    # Traffic Provider Settings (demo | tomtom | google | unavailable)
    TRAFFIC_PROVIDER: str = os.getenv("TRAFFIC_PROVIDER", "demo")
    TRAFFIC_API_KEY: Optional[str] = os.getenv("TRAFFIC_API_KEY", None)

    # Dynamic Pressure Refresh Settings
    PRESSURE_REFRESH_INTERVAL_SECONDS: int = int(os.getenv("PRESSURE_REFRESH_INTERVAL_SECONDS", "300"))

    # AI Provider Settings (SIH 2026: mock default ensures zero-API-key seamless demo)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")
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


