"""
Historical Tourism & Crowd Intelligence API (Milestone 10 / Prompt 3).

Exposes additive, backward-compatible endpoints for:
1. Historical observation queries
2. Dataset status & availability metrics
3. Signal-level provenance audit summaries
4. Live observation persistence / ingestion
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.historical import (
    HistoricalObservationRecord,
    DatasetMetadata,
)
from app.services.historical.ingestion_service import historical_ingestion_service
from app.services.historical.backfill_service import historical_backfill_service

router = APIRouter(prefix="/historical", tags=["Historical Tourism Data Foundation"])


@router.get("/status", summary="Get historical tourism data foundation status")
def get_historical_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Returns storage status, dialect, total records, and ML readiness threshold."""
    return historical_ingestion_service.get_status(db=db)


@router.get("/observations", response_model=List[HistoricalObservationRecord], summary="Query time-aligned historical observations")
def query_observations(
    destination_id: Optional[str] = Query(None, description="Optional destination identifier filter"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    dataset_mode: Optional[str] = Query(None, description="REAL, SYNTHETIC, or MIXED"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    db: Session = Depends(get_db)
) -> List[HistoricalObservationRecord]:
    """Query time-aligned observations with strict signal-level provenance."""
    return historical_ingestion_service.get_observations(
        destination_id=destination_id,
        start_date=start_date,
        end_date=end_date,
        dataset_mode=dataset_mode,
        limit=limit,
        db=db
    )


@router.get("/latest", response_model=Optional[HistoricalObservationRecord], summary="Get latest persisted observation")
def get_latest_observation(
    destination_id: str = Query(..., description="Destination identifier (e.g. 'darjeeling')"),
    dataset_mode: str = Query("REAL", description="REAL, SYNTHETIC, or MIXED"),
    db: Session = Depends(get_db)
) -> Optional[HistoricalObservationRecord]:
    """Fetch the most recent persisted observation for a destination."""
    rec = historical_ingestion_service.get_latest_observation(
        destination_id=destination_id,
        dataset_mode=dataset_mode,
        db=db
    )
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {dataset_mode} observation found for destination '{destination_id}'"
        )
    return rec


@router.get("/provenance", summary="Get provenance audit breakdown")
def get_provenance_summary(
    destination_id: Optional[str] = Query(None, description="Optional destination filter"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Returns provenance distribution counts and signal availability percentages."""
    return historical_ingestion_service.get_provenance_summary(
        destination_id=destination_id,
        db=db
    )


@router.post("/ingest", summary="Capture and persist current observation")
def ingest_current_observation(
    destination_id: Optional[str] = Query(None, description="Destination ID, or omit for all canonical destinations"),
    date_bucket: Optional[str] = Query(None, description="Observation date bucket YYYY-MM-DD (defaults to UTC today)"),
    dataset_mode: str = Query("REAL", description="Classification: REAL, SYNTHETIC, MIXED"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Samples live telemetry and Crowd Engine V2 output to persist observations.
    Strictly idempotent: repeated calls on the same destination and date update without duplicate rows.
    """
    if destination_id:
        rec = historical_ingestion_service.capture_current_observation(
            destination_id=destination_id,
            date_bucket=date_bucket,
            dataset_mode=dataset_mode,
            db=db
        )
        return {
            "status": "SUCCESS",
            "message": f"Successfully ingested {dataset_mode} observation for {rec.destination_id}",
            "observation": rec.model_dump()
        }
    else:
        records = historical_ingestion_service.capture_all_destinations(
            date_bucket=date_bucket,
            dataset_mode=dataset_mode,
            db=db
        )
        return {
            "status": "SUCCESS",
            "message": f"Successfully ingested observations for {len(records)} destinations",
            "count": len(records),
            "destinations": [r.destination_id for r in records]
        }


@router.post("/backfill", summary="Run historical data backfill")
def run_historical_backfill(
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    destinations: Optional[List[str]] = Query(None, description="Optional list of destination IDs to backfill"),
    dataset_mode: str = Query("REAL", description="Classification: REAL, SYNTHETIC, or MIXED"),
    dry_run: bool = Query(True, description="When true, simulates backfill without committing database changes"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Idempotent historical backfill mechanism extracting genuine first-party telemetry
    (PostgreSQL confirmed bookings, verified demand events, gazetted holidays, regional events).
    Strictly preserves provenance and enforces canonical destination mapping.
    """
    return historical_backfill_service.backfill_historical_data(
        start_date=start_date,
        end_date=end_date,
        destinations=destinations,
        dataset_mode=dataset_mode,
        dry_run=dry_run,
        db=db
    )


@router.get("/quality-report", summary="Generate historical dataset quality & leakage report")
def get_historical_quality_report(
    dataset_mode: str = Query("REAL", description="Classification: REAL, SYNTHETIC, or MIXED"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Generates an automated quality report covering:
    - Coverage (total rows, unique destinations, temporal span, rows per day/dest)
    - Signal completeness (populated vs missingness %, signal-level provenance breakdown)
    - Target quality (distribution, variance, min, max, mean)
    - Leakage checks (future target leakage count, duplicate pairs, invalid timestamps)
    """
    return historical_backfill_service.generate_quality_report(
        dataset_mode=dataset_mode,
        db=db
    )


@router.post("/daily-capture", summary="Execute scheduled daily observation capture")
def run_daily_capture(
    date_bucket: Optional[str] = Query(None, description="Observation date bucket YYYY-MM-DD (defaults to UTC today)"),
    dataset_mode: str = Query("REAL", description="Classification: REAL, SYNTHETIC, or MIXED"),
    max_retries: int = Query(3, ge=1, le=5, description="Maximum retry attempts per destination"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Executes idempotent daily observation capture across all canonical destinations
    with retry handling, failure logging, and strict provenance enforcement.
    """
    return historical_ingestion_service.run_daily_scheduled_capture(
        date_bucket=date_bucket,
        dataset_mode=dataset_mode,
        max_retries=max_retries,
        db=db
    )


@router.get("/capture-status", summary="Get data accumulation scheduler status")
def get_historical_capture_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns scheduler accumulation status:
    - last_capture timestamp
    - next_recommended_capture timestamp
    - successful_destinations
    - failed_destinations
    - signals_available
    - signals_unavailable
    - rows_captured
    - rows_updated
    - rows_created
    """
    return historical_ingestion_service.get_capture_status(db=db)


@router.get("/coverage", summary="Get six-destination coverage and representation report")
def get_historical_coverage(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns per-destination coverage metrics for all six canonical destinations:
    - real_rows count
    - distinct dates
    - first & latest observation dates
    - days since latest observation
    - latest observation quality grade
    - available and missing signal counts
    - underrepresented destination flags (<20 rows)
    """
    from app.services.historical.readiness_service import historical_readiness_service
    return historical_readiness_service.get_destination_coverage(db=db)

