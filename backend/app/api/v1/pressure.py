"""
Pressure Intelligence Endpoints for Yatri Setu.
GET /api/destinations/{id}/pressure
GET /api/destinations/{id}/pressure/forecast
GET /api/destinations/{id}/pressure/evidence
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.pressure import PressureResponse, ForecastResponse
from app.models.observation import PressureEvidenceResponse, PressureEvidenceV2
from app.services.crowd_engine_v2 import crowd_engine_v2

router = APIRouter(prefix="/destinations", tags=["Destination Pressure V2"])


@router.get("/{destination_id}/pressure", response_model=PressureResponse)
def get_destination_pressure(
    destination_id: str,
    date: Optional[str] = Query(None, description="Optional target date in YYYY-MM-DD format")
):
    """
    Returns multi-signal pressure response across 8 data sources,
    with transparency confidence scores and signal breakdowns.
    """
    return crowd_engine_v2.calculate_pressure(destination_id, date)


@router.get("/{destination_id}/pressure/forecast", response_model=ForecastResponse)
def get_destination_pressure_forecast(
    destination_id: str,
    days: int = Query(7, ge=1, le=14, description="Forecast window in days")
):
    """
    Returns 7-day predictive pressure forecast with key drivers,
    weekend spikes, and regional holiday detection.
    """
    return crowd_engine_v2.calculate_pressure_forecast(destination_id, days)


@router.get("/{destination_id}/pressure/evidence", response_model=PressureEvidenceResponse)
def get_destination_pressure_evidence(
    destination_id: str,
    date: Optional[str] = Query(None, description="Optional target date in YYYY-MM-DD format")
):
    """
    Returns full evidence audit trail with raw values, normalized scores,
    mathematical weights, provider modes (MOCK/REAL/CACHED), and confidence ratings.
    Consumed by the Evidence Drawer panel in the Command Center.
    """
    return crowd_engine_v2.get_pressure_evidence_v2(destination_id, date)
