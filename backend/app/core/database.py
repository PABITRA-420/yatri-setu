import logging
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure engine with dialect-specific options
engine_kwargs: Dict[str, Any] = {
    "pool_pre_ping": True,
    "echo": False,
}

if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production PostgreSQL connection pool settings
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_timeout"] = settings.DB_POOL_TIMEOUT
    engine_kwargs["pool_recycle"] = settings.DB_POOL_RECYCLE

engine = create_engine(
    settings.DATABASE_URL,
    **engine_kwargs
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

def _migrate_sqlite_columns() -> None:
    """Ensures existing local development SQLite database schema reflects newly added model columns."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        # Check homestays
        if "homestays" in table_names:
            cols = {c["name"] for c in inspector.get_columns("homestays")}
            with engine.connect() as conn:
                for col, defn in [
                    ("title", "VARCHAR(128)"),
                    ("tagline", "VARCHAR(256)"),
                    ("address", "VARCHAR(256)"),
                    ("room_type", "VARCHAR(64) DEFAULT 'Standard Room'"),
                    ("rating", "FLOAT DEFAULT 5.0"),
                    ("reviews_count", "INTEGER DEFAULT 0"),
                    ("verification_status", "VARCHAR(32) DEFAULT 'VERIFIED'"),
                    ("is_published", "BOOLEAN DEFAULT 1"),
                    ("village", "VARCHAR(128)"),
                    ("panchayat_name", "VARCHAR(128)"),
                    ("special_activity", "VARCHAR(256)"),
                    ("amenities_json", "JSON"),
                    ("images_json", "JSON"),
                ]:
                    if col not in cols:
                        conn.execute(text(f"ALTER TABLE homestays ADD COLUMN {col} {defn}"))
                conn.commit()

        # Check bookings
        if "bookings" in table_names:
            cols = {c["name"] for c in inspector.get_columns("bookings")}
            with engine.connect() as conn:
                for col, defn in [
                    ("traveler_phone", "VARCHAR(32)"),
                    ("traveler_email", "VARCHAR(128)"),
                    ("emergency_contact", "VARCHAR(32)"),
                    ("rooms_booked", "INTEGER DEFAULT 1"),
                    ("failure_reason", "VARCHAR(64)"),
                    ("failure_detail", "TEXT"),
                    ("idempotency_key", "VARCHAR(128)"),
                    ("digital_pass_qr_payload", "TEXT"),
                    ("transitions_json", "JSON"),
                    ("updated_at", "DATETIME"),
                ]:
                    if col not in cols:
                        conn.execute(text(f"ALTER TABLE bookings ADD COLUMN {col} {defn}"))
                conn.commit()

        # Check availability
        if "availability" in table_names:
            cols = {c["name"] for c in inspector.get_columns("availability")}
            with engine.connect() as conn:
                for col, defn in [
                    ("total_units", "INTEGER DEFAULT 2"),
                    ("booked_units", "INTEGER DEFAULT 0"),
                    ("updated_at", "DATETIME"),
                ]:
                    if col not in cols:
                        conn.execute(text(f"ALTER TABLE availability ADD COLUMN {col} {defn}"))
                conn.commit()

        # Check safety_incidents
        if "safety_incidents" in table_names:
            cols = {c["name"] for c in inspector.get_columns("safety_incidents")}
            with engine.connect() as conn:
                for col, defn in [
                    ("trip_id", "VARCHAR(64)"),
                    ("traveler_session_id", "VARCHAR(128)"),
                    ("user_name", "VARCHAR(128)"),
                    ("user_phone", "VARCHAR(32)"),
                    ("status", "VARCHAR(32) DEFAULT 'DELIVERED'"),
                    ("notes", "TEXT"),
                    ("escalation_level", "INTEGER DEFAULT 0"),
                    ("idempotency_key", "VARCHAR(128)"),
                    ("audit_trail_json", "JSON"),
                    ("notifications_json", "JSON"),
                ]:
                    if col not in cols:
                        conn.execute(text(f"ALTER TABLE safety_incidents ADD COLUMN {col} {defn}"))
                conn.commit()
    except Exception as exc:
        logger.debug(f"SQLite column migration notice: {exc}")

def init_db() -> None:
    """Initialize all registered SQLAlchemy tables with graceful error handling."""
    try:
        Base.metadata.create_all(bind=engine)
        _migrate_sqlite_columns()
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
    is_sqlite = (dialect_name == "sqlite")
    configured = bool(settings.DATABASE_URL)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "configured": configured,
            "reachable": True,
            "dialect": dialect_name,
            "is_sqlite": is_sqlite
        }
    except Exception as exc:
        logger.warning(f"Database health check probe failed: {exc}")
        return {
            "status": "degraded",
            "configured": configured,
            "reachable": False,
            "dialect": dialect_name,
            "is_sqlite": is_sqlite,
            "notice": "Database connection probe failed; platform operating in fallback mode"
        }
