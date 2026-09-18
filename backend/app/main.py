import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import init_db, check_database_health
from app.core.logging import setup_safe_logging
from app.api.v1.api import api_router
import app.models.entities  # Register all models

logger = logging.getLogger(__name__)

# Initialize safe logging filter
setup_safe_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
def on_startup():
    try:
        init_db()
        from app.services.homestay_repository import homestay_repository
        homestay_repository.sync_to_db()
    except Exception as e:
        logger.warning(f"Startup database initialization deferred: {e}")


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for unhandled internal errors (prevents stack trace / credential leak)
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error processing {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal operational error occurred. Telemetry has been logged safely."}
    )

# Exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed", "errors": exc.errors()}
    )

# Mount API (supporting both /api and /api/v1)
app.include_router(api_router, prefix=settings.API_V1_STR)
if settings.API_V1_STR != "/api/v1":
    app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def root():
    return {
        "project": "Yatri Setu",
        "version": settings.VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "hackathon": "Smart India Hackathon 2026",
        "core_differentiator": "Smart Crowd Management & Alternate-Destination Advisor",
        "docs_url": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check(detailed: bool = False):
    """
    Concise health probe for load balancers and backward-compatible tests.
    Pass ?detailed=true for full operational provider status.
    """
    if not detailed:
        return {"status": "healthy"}
    return get_detailed_health()

@app.get("/api/health", tags=["Health"])
def api_health_check(detailed: bool = True):
    """
    Safe operational health probe for Render, Vercel, and monitoring systems.
    Strictly reports status and provenance without leaking secrets or credentials.
    """
    if not detailed:
        return {"status": "healthy"}
    return get_detailed_health()

def get_detailed_health():
    from app.services.weather.service import weather_service
    from app.services.traffic.service import traffic_service
    from app.services.routing.service import routing_service

    db_health = check_database_health()
    
    weather_mode = weather_service._provider.get_provider_mode()
    weather_avail = weather_service._provider.is_available()

    routing_mode = routing_service.get_provider_mode()
    routing_avail = routing_service.is_available()

    traffic_mode = traffic_service._provider.get_provider_mode()
    traffic_avail = traffic_service._provider.is_available()
    if traffic_mode == "REAL":
        traffic_provenance = "REAL — TOMTOM TRAFFIC" if traffic_avail else "UNAVAILABLE — SAFE FALLBACK"
        traffic_reported_mode = "REAL" if traffic_avail else "UNAVAILABLE"
    elif traffic_mode == "UNAVAILABLE":
        traffic_provenance = "UNAVAILABLE — SAFE FALLBACK"
        traffic_reported_mode = "UNAVAILABLE"
    else:
        traffic_provenance = "DEMO MODE — SYNTHETIC DATA"
        traffic_reported_mode = "DEMO"

    ai_provider = settings.AI_PROVIDER.lower().strip()
    if ai_provider == "gemini":
        ai_configured = bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
        ai_model = settings.GEMINI_MODEL
    elif ai_provider == "groq":
        ai_configured = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())
        ai_model = settings.GROQ_MODEL
    elif ai_provider == "openai":
        ai_configured = bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())
        ai_model = settings.OPENAI_MODEL
    else:
        ai_configured = True
        ai_model = "mock_adaptive"

    fallback_configured = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip()) if settings.AI_FALLBACK_PROVIDER == "groq" else True

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_health,
        "providers": {
            "weather": {
                "provider": settings.WEATHER_PROVIDER,
                "mode": weather_mode,
                "available": weather_avail,
                "provenance": "REAL — EXTERNAL PROVIDER" if weather_mode == "REAL" else "DEMO MODE — SYNTHETIC DATA"
            },
            "routing": {
                "provider": settings.ROUTING_PROVIDER,
                "mode": routing_mode,
                "available": routing_avail,
                "provenance": "REAL — OSRM (OPENSTREETMAP)" if routing_mode == "osrm" else "DEMO MODE — SYNTHETIC DATA"
            },
            "ai": {
                "provider": settings.AI_PROVIDER,
                "fallback_provider": settings.AI_FALLBACK_PROVIDER,
                "model": ai_model,
                "configured": ai_configured,
                "fallback_configured": fallback_configured
            },
            "traffic": {
                "provider": settings.TRAFFIC_PROVIDER,
                "mode": traffic_reported_mode,
                "available": traffic_avail,
                "provenance": traffic_provenance
            }
        },
        "routing": {
            "provider": settings.ROUTING_PROVIDER,
            "mode": routing_mode,
            "available": routing_avail,
            "provenance": "REAL — OSRM (OPENSTREETMAP)" if routing_mode == "osrm" else "DEMO MODE — SYNTHETIC DATA"
        },
        "weather": {
            "provider": settings.WEATHER_PROVIDER,
            "mode": weather_mode,
            "available": weather_avail,
            "provenance": "REAL — EXTERNAL PROVIDER" if weather_mode == "REAL" else "DEMO MODE — SYNTHETIC DATA"
        },
        "traffic": {
            "provider": settings.TRAFFIC_PROVIDER,
            "mode": traffic_reported_mode,
            "available": traffic_avail,
            "provenance": traffic_provenance
        },
        "provenance_policy": {
            "zero_key_demo_supported": True,
            "real_data_distinguished": True,
            "pii_protection": "STRICT_ZERO_PII_HOST_PANCHAYAT"
        }
    }
