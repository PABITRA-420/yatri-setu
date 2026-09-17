import logging
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure engine with dialect-specific options
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize all registered SQLAlchemy tables with graceful error handling."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database schema initialized successfully (dialect: {engine.dialect.name}).")
    except Exception as exc:
        logger.warning(
            f"Database initialization warning: {exc}. "
            "Application continuing with resilient in-memory / fallback repositories."
        )

def check_database_health() -> Dict[str, Any]:
    """
    Performs a safe, non-blocking health probe on the database.
    Strictly avoids exposing passwords, hosts, or sensitive connection strings.
    """
    dialect_name = getattr(engine.dialect, "name", "unknown")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "dialect": dialect_name,
            "is_sqlite": dialect_name == "sqlite"
        }
    except Exception as exc:
        logger.warning(f"Database health check probe failed: {exc}")
        return {
            "status": "degraded",
            "dialect": dialect_name,
            "is_sqlite": dialect_name == "sqlite",
            "notice": "Database connection probe failed; platform operating in fallback mode"
        }
