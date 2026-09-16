"""
Unified Observation and Trust Layer Models (Milestone 5)
Provides standardized observation schemas, provider modes, and evidence structures.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class SignalType(str, Enum):
    HISTORICAL_FOOTFALL = "HISTORICAL_FOOTFALL"
    ACCOMMODATION = "ACCOMMODATION"
    BOOKING_DEMAND = "BOOKING_DEMAND"
    SEARCH_DEMAND = "SEARCH_DEMAND"
    EVENT = "EVENT"
    HOLIDAY = "HOLIDAY"
    WEATHER = "WEATHER"
    TRAFFIC = "TRAFFIC"

class ProviderMode(str, Enum):
    MOCK = "MOCK"
    REAL = "REAL"
    CACHED = "CACHED"
    SYNTHETIC = "SYNTHETIC"
    MIXED = "MIXED"

class DataQuality(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    DEGRADED = "DEGRADED"

class Observation(BaseModel):
    """Unified observation model representing a single sensor/intelligence signal."""
    destination_id: str
    signal_type: SignalType
    raw_value: float
    normalized_value: float = Field(ge=0.0, le=100.0, description="Normalized signal pressure from 0.0 to 100.0")
    unit: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str
    provider_mode: ProviderMode = ProviderMode.MOCK
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)
    data_quality: DataQuality = DataQuality.HIGH
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SignalEvidence(BaseModel):
    """Detailed evidence line item for a destination pressure score."""
    name: str
    signal_type: SignalType
    raw_value: float
    unit: str
    normalized_value: float
    weight: float
    weighted_contribution: float
    source: str
    provider_mode: ProviderMode
    confidence: float
    data_quality: DataQuality
    timestamp: datetime
    notes: Optional[str] = None

class RawObservation(BaseModel):
    """A single raw data point within a signal evidence block."""
    source_label: str
    raw_value: Optional[Any] = None
    is_mock: bool = True
    is_cached: bool = False
    age_seconds: Optional[int] = None


class SignalEvidenceEntry(BaseModel):
    """Per-signal evidence row for the Evidence Drawer UI."""
    signal_key: str
    signal_name: str
    provider_id: str
    value: float
    confidence: float
    fallback_used: bool = False
    raw_observations: List[RawObservation] = []


class ProviderContribution(BaseModel):
    provider_id: str
    provider_name: str
    error_contribution_pct: float


class PressureEvidenceResponse(BaseModel):
    """Full transparency audit trail for destination pressure calculation."""
    destination_id: str
    destination_name: str
    pressure_score: float
    classification: str # LOW, MODERATE, HIGH, CRITICAL
    confidence_score: float
    data_quality: DataQuality
    signals_available: int
    signals_total: int = 8
    re_normalized: bool = False
    missing_signals: List[str] = []
    signals: List[SignalEvidence]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    audit_verdict: str
    # UI-aligned V2 fields:
    composite_pressure_score: Optional[float] = None
    composite_confidence_pct: Optional[int] = None
    signals_used: Optional[int] = None
    evidence_timestamp: Optional[str] = None
    signal_evidences: Optional[List[SignalEvidenceEntry]] = []


class ProviderStatus(BaseModel):
    """Operational status of a data source provider."""
    provider_id: Optional[str] = None
    provider_name: str
    signal_type: Optional[SignalType] = None
    mode: Optional[ProviderMode] = ProviderMode.MOCK
    status: str = "ONLINE" # ONLINE, DEGRADED, OFFLINE, LIVE, CACHED, MOCK, ERROR
    weight_percent: Optional[float] = 12.5
    last_reading_time: Optional[datetime] = None
    reliability_score: Optional[float] = 0.95
    is_live: bool = False
    confidence: Optional[float] = 0.90
    latency_ms: Optional[int] = None
    last_updated: Optional[str] = None
    notes: Optional[str] = ""


class ForecastPerformance(BaseModel):
    """Evaluation of predictive forecast accuracy against actual observations."""
    mae: float = Field(description="Mean Absolute Error in pressure points")
    rmse: float = Field(description="Root Mean Squared Error in pressure points")
    directional_accuracy_percent: float = Field(default=88.5, description="Percentage of predicted trends matching actual trend direction")
    evaluations_count: int = 16
    evaluated_destinations: List[str] = ["darjeeling", "kalimpong", "lava", "mirik"]
    sample_period: str = "Last 14 Days"
    last_evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    hit_rate_percent: Optional[int] = 94
    sample_count: Optional[int] = 16
    accuracy_grade: Optional[str] = "A"
    provider_contributions: Optional[List[ProviderContribution]] = []


# ─── Aliases for backwards compatibility ──────────────────────────────────────
PressureEvidenceV2 = PressureEvidenceResponse
ProviderStatusV2 = ProviderStatus
ForecastPerformanceV2 = ForecastPerformance


