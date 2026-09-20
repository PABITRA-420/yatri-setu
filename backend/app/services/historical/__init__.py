"""
Historical Tourism & Crowd Intelligence Foundation (Milestone 10 / Prompt 3).

Establishes:
1. Signal-level provenance classification and telemetry tracking.
2. Canonical daily time-bucket alignment.
3. PostgreSQL/SQLite historical crowd observation persistence.
4. Separate REAL, SYNTHETIC, and MIXED dataset modes.
5. Strict temporal leakage prevention for future ML forecasting.
"""

from app.services.historical.ingestion_service import (
    HistoricalIngestionService,
    historical_ingestion_service,
)

__all__ = [
    "HistoricalIngestionService",
    "historical_ingestion_service",
]
