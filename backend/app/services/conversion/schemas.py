"""
Conversion Funnel and First-Party Intelligence Schemas for Yatri Setu (Milestone 7E).
Defines normalized conversion metrics, funnel stages, observed acceptance rates, and provenance.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AcceptanceRateMode(str, Enum):
    CONFIGURED = "CONFIGURED"               # Using simulation baseline parameter (0.15)
    OBSERVED = "OBSERVED"                   # Sufficient first-party sample size (>= 20)
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA" # Telemetry exists but below statistical significance


class DestinationConversionMetrics(BaseModel):
    destination_id: str
    destination_name: str
    searches: int = 0
    date_selections: int = 0
    alternative_views: int = 0
    alternative_acceptances: int = 0
    availability_checks: int = 0
    booking_initiations: int = 0
    booking_confirmations: int = 0
    booking_cancellations: int = 0
    outbound_clicks: int = 0
    # Calculated rates (0.0 to 1.0)
    search_to_availability_rate: float = 0.0
    availability_to_booking_rate: float = 0.0
    booking_to_confirmation_rate: float = 0.0
    alternative_acceptance_rate: float = 0.0
    cancellation_rate: float = 0.0


class FunnelStageCount(BaseModel):
    stage: str = Field(..., description="Funnel step name")
    count: int = Field(..., description="Headcount or event count at this stage")
    conversion_from_previous: float = Field(..., ge=0.0, le=100.0, description="Step conversion %")
    conversion_from_top: float = Field(..., ge=0.0, le=100.0, description="Overall funnel conversion %")


class ConversionSummaryResponse(BaseModel):
    circuit_metrics: DestinationConversionMetrics
    destination_metrics: List[DestinationConversionMetrics]
    funnel: List[FunnelStageCount]
    observed_acceptance_rate: float
    configured_acceptance_rate: float
    acceptance_rate_mode: AcceptanceRateMode
    sample_size: int
    data_quality_warning: Optional[str] = None
    provenance: str = Field("REAL — YATRI SETU NETWORK", description="First-party telemetry provenance")
    generated_at: str
