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
