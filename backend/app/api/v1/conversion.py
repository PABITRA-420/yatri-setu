"""
Conversion & First-Party Analytics Endpoints for Yatri Setu (Milestone 7E).
Provides conversion funnel summaries, destination-level metrics, and telemetry ingestion.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from app.services.conversion.schemas import (
    ConversionSummaryResponse,
    DestinationConversionMetrics,
    FunnelStageCount,
)
from app.services.conversion.funnel_service import conversion_funnel_service
from app.services.demand_aggregation_service import demand_aggregation_service
from app.models.demand import DemandEventType

router = APIRouter(tags=["First-Party Conversion & Telemetry"])


class TelemetryEventRequest(BaseModel):
    event_type: str = Field(..., description="Event type (e.g. outbound_booking_click, alternative_viewed)")
    destination_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.get("/admin/conversion/summary", response_model=ConversionSummaryResponse)
def get_conversion_summary():
    """
    Returns macro first-party conversion intelligence overview across the entire circuit,
    including step-by-step conversion funnel, observed acceptance rate, and sample size.
    """
    return conversion_funnel_service.get_conversion_summary()


@router.get("/admin/conversion/destinations", response_model=List[DestinationConversionMetrics])
def get_destination_conversion_metrics(
    destination_id: Optional[str] = Query(None, description="Optional destination filter")
):
    """
    Returns destination-level conversion counts and derived conversion rates.
    """
    return conversion_funnel_service.get_destination_conversion_metrics(destination_id=destination_id)


@router.get("/admin/conversion/funnel", response_model=List[FunnelStageCount])
def get_conversion_funnel():
    """
    Returns the normalized circuit-wide conversion funnel stages.
    """
    return conversion_funnel_service.get_funnel()


@router.get("/admin/conversion/alternatives")
def get_alternative_conversion_analytics():
    """
    Returns destination-specific alternative funnel intelligence:
    alternatives shown -> clicked -> accepted -> availability checked -> booked -> confirmed.
    """
    summary = conversion_funnel_service.get_conversion_summary()
    return {
        "observed_acceptance_rate": summary.observed_acceptance_rate,
        "configured_acceptance_rate": summary.configured_acceptance_rate,
        "mode": summary.acceptance_rate_mode.value,
        "sample_size": summary.sample_size,
        "destinations": [
            {
                "destination_id": m.destination_id,
                "destination_name": m.destination_name,
                "alternative_views": m.alternative_views,
                "alternative_acceptances": m.alternative_acceptances,
                "acceptance_rate": m.alternative_acceptance_rate,
                "availability_checks": m.availability_checks,
                "booking_initiations": m.booking_initiations,
                "booking_confirmations": m.booking_confirmations,
                "provenance": "REAL — YATRI SETU NETWORK"
            }
            for m in summary.destination_metrics
        ],
        "generated_at": datetime.utcnow().isoformat()
    }


@router.post("/conversion/events")
def record_conversion_event(req: TelemetryEventRequest):
    """
    Client endpoint to record normalized first-party user intent telemetry
    (e.g., alternative_viewed, date_selected, destination_view, outbound_booking_click).
    Strictly excludes sensitive personal or payment information.
    """
    clean_type = req.event_type.lower().strip()
    return demand_aggregation_service.record_event(
        event_type=clean_type,
        destination_id=req.destination_id,
        session_id=req.session_id,
        metadata=req.metadata,
        is_synthetic=False,
        source="YATRI_SETU_FRONTEND"
    )
