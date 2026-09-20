"""
Data models for canonical Historical Tourism & Crowd Observations (Milestone 10 / Prompt 3).

Establishes:
1. Signal-level provenance classification (LIVE, CACHED, HISTORICAL, COMPUTED, SYNTHETIC, DEMO, UNAVAILABLE).
2. Time-aligned historical observation schemas with explicit NULLability for unmeasured signals.
3. Dataset metadata models making data composition transparent to ML pipelines.
4. Leakage-prevention attributes separating feature timestamp, target timestamp, and target horizon.
"""
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, ConfigDict

from app.services.data_sources.base import VALID_PROVIDER_MODES


class SignalProvenanceRecord(BaseModel):
    """Provenance audit trail for an individual telemetry signal."""
    source: str = Field(..., description="Provider source identifier (e.g. LIVE_OPENWEATHERMAP_API, POSTGRESQL_BOOKINGS)")
    provider_mode: str = Field(..., description="Classification: LIVE, CACHED, HISTORICAL, COMPUTED, SYNTHETIC, DEMO, UNAVAILABLE")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    is_available: bool = Field(True, description="Whether this signal was actively measured")
    raw_value: Optional[float] = None
    raw_unit: Optional[str] = None
    notes: Optional[str] = None

    def validate_mode(self):
        if self.provider_mode.upper() not in VALID_PROVIDER_MODES:
            raise ValueError(f"Invalid provider_mode '{self.provider_mode}'. Must be one of {VALID_PROVIDER_MODES}")


class HistoricalObservationBase(BaseModel):
    destination_id: str = Field(..., description="Destination identifier (e.g. 'darjeeling')")
    observed_at: datetime = Field(..., description="Timestamp of observation")
    date_bucket: str = Field(..., description="Canonical daily time bucket YYYY-MM-DD")
    
    # Signals are explicitly Optional — missing signals remain None (never manufactured)
    footfall: Optional[float] = Field(None, description="Tourist footfall volume or index (NULL if unmeasured)")
    accommodation_occupancy: Optional[float] = Field(None, description="Occupancy percentage 0-100 (NULL if unmeasured)")
    booking_demand: Optional[float] = Field(None, description="Forward booking pace/velocity (NULL if unmeasured)")
    search_demand: Optional[float] = Field(None, description="Leading search query index (NULL if unmeasured)")
    traffic_pressure: Optional[float] = Field(None, description="Corridor traffic congestion score 0-100 (NULL if unmeasured)")
    weather_pressure: Optional[float] = Field(None, description="Weather pressure favorability index 0-100 (NULL if unmeasured)")
    holiday_pressure: Optional[float] = Field(None, description="Calendar holiday surge index 0-100 (NULL if unmeasured)")
    event_pressure: Optional[float] = Field(None, description="Local event/festival pressure index 0-100 (NULL if unmeasured)")
    current_crowd_pressure: Optional[float] = Field(None, description="Canonical Crowd Engine V2 current pressure score 0-100")

    # Calendar & Event Context
    is_weekend: bool = Field(False, description="Whether date falls on weekend (Fri/Sat/Sun)")
    is_holiday: bool = Field(False, description="Whether date is a gazetted or festival holiday")
    holiday_name: Optional[str] = Field(None, description="Name of holiday if applicable")
    active_events_count: int = Field(0, description="Count of active local cultural/sports events")

    # Provenance tracking
    signal_provenance: Dict[str, SignalProvenanceRecord] = Field(
        default_factory=dict,
        description="Signal-level provenance dictionary mapping signal_name to SignalProvenanceRecord"
    )
    data_status: str = Field("PARTIAL", description="Overall data status: COMPLETE, PARTIAL, DEGRADED, UNAVAILABLE, SYNTHETIC")
    dataset_mode: str = Field("REAL", description="Classification: REAL, SYNTHETIC, MIXED")
    composite_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Overall confidence across available signals")


class HistoricalObservationCreate(HistoricalObservationBase):
    pass


class HistoricalObservationRecord(HistoricalObservationBase):
    id: str = Field(..., description="Unique record identifier / idempotency key")
    ingested_at: datetime = Field(..., description="Timestamp when record was persisted")

    model_config = ConfigDict(from_attributes=True)


class DatasetMetadata(BaseModel):
    """
    Audit metadata describing the provenance composition and quality of an ML training dataset.
    Prevents models trained on synthetic data from masquerading as trained on real historical data.
    """
    dataset_mode: str = Field(..., description="REAL | SYNTHETIC | MIXED")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    destination_count: int = Field(..., description="Number of unique destinations included")
    destinations: List[str] = Field(default_factory=list)
    row_count: int = Field(..., description="Total training rows")
    time_start: str = Field(..., description="Start of observation period YYYY-MM-DD")
    time_end: str = Field(..., description="End of observation period YYYY-MM-DD")
    
    # Composition breakdown
    real_row_count: int = Field(0, description="Count of genuine historical rows")
    synthetic_row_count: int = Field(0, description="Count of synthetic benchmark rows")
    mixed_row_count: int = Field(0, description="Count of mixed rows")
    
    # Signal quality & availability
    signal_availability_percentages: Dict[str, Any] = Field(
        default_factory=dict,
        description="Percentage of non-NULL observations for each signal or nested breakdown"
    )

    provenance_counts: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of signals by provenance mode (LIVE, CACHED, HISTORICAL, COMPUTED, SYNTHETIC, DEMO, UNAVAILABLE)"
    )
    unavailable_signal_count: int = Field(0, description="Count of NULL or UNAVAILABLE signal slots")
    
    # ML readiness & leakage prevention
    ml_eligible: bool = Field(False, description="Whether dataset meets the minimum historical threshold for ML training")
    target_horizon_days: Union[int, List[int]] = Field(1, description="Forecasting horizon (H days ahead) or list of horizons")
    leakage_prevention_verified: bool = Field(True, description="Strict verification that target timestamps are strictly > feature timestamps")
    notes: str = Field("", description="Human-readable transparency notes")
