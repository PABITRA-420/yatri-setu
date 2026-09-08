"""
Dataset Evaluation & Baseline Performance Models (Milestone 6A).
Covers historical crowd observation records, data quality validation reports,
chronological train/validation/test metrics, and ML feasibility verdicts.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HistoricalObservation(BaseModel):
    """
    Standardized observation schema for historical crowd intelligence.
    Explicitly tracks origin source to ensure synthetic demo data is never presented as real.
    """
    date: str = Field(description="Observation date in YYYY-MM-DD format")
    destination_id: str = Field(description="Target destination identifier")
    historical_footfall: float = Field(ge=0.0, le=100.0)
    accommodation_occupancy: float = Field(ge=0.0, le=100.0)
    booking_demand: float = Field(ge=0.0, le=100.0)
    search_demand: float = Field(ge=0.0, le=100.0)
    event_pressure: float = Field(ge=0.0, le=100.0)
    holiday_pressure: float = Field(ge=0.0, le=100.0)
    weather_pressure: float = Field(ge=0.0, le=100.0)
    traffic_pressure: float = Field(ge=0.0, le=100.0)
    observed_pressure: float = Field(ge=0.0, le=100.0, description="Ground truth crowd pressure observation")
    source: str = Field(default="SYNTHETIC_GENERATOR", description="Data provenance label")
    data_quality: str = Field(default="HIGH", description="Quality rating: HIGH, MEDIUM, LOW, DEGRADED")
    confidence: float = Field(ge=0.0, le=1.0, default=0.92)


class DataQualityCheckResult(BaseModel):
    """Individual data quality rule execution result."""
    name: str
    passed: bool
    detail: str
    anomalies_detected: int = 0


class DataQualityReport(BaseModel):
    """Full data quality inspection report for the historical observation dataset."""
    dataset_mode: str = Field(default="SYNTHETIC DEMO", description="Transparency label: SYNTHETIC DEMO / REAL / MIXED")
    total_records: int
    destinations_count: int
    date_range: Dict[str, str]
    completeness_score: float = Field(description="Percentage of clean, complete observations")
    quality_rating: str = Field(description="HIGH | MEDIUM | LOW | DEGRADED")
    checks: List[DataQualityCheckResult]
    is_valid: bool
    summary: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class ChronologicalSplitMetrics(BaseModel):
    """Evaluation metrics for a strictly ordered time-series segment (no data leakage)."""
    split_name: str
    start_date: str
    end_date: str
    sample_count: int
    mae: float
    rmse: float
    directional_accuracy: float


class DestinationErrorMetrics(BaseModel):
    """Error metrics partitioned by destination archetype."""
    destination_id: str
    destination_name: str
    sample_count: int
    mae: float
    rmse: float
    directional_accuracy: float


class SeasonErrorMetrics(BaseModel):
    """Error metrics partitioned by Himalayan climatic & tourism seasons."""
    season_name: str
    period_label: str
    sample_count: int
    mae: float
    rmse: float
    directional_accuracy: float


class DataSufficiencyVerdict(BaseModel):
    """Assessment of whether historical dataset is sufficient to justify ML training."""
    is_sufficient: bool
    confidence: str
    sample_size_adequate: bool
    seasonality_represented: bool
    signal_coverage_complete: bool
    recommendation: str
    rationale: str


class BaselineEvaluationReport(BaseModel):
    """Comprehensive benchmark of deterministic Crowd Engine V2 against historical observations."""
    dataset_size: int
    date_range: Dict[str, str]
    destinations: List[str]
    dataset_mode: str = Field(default="SYNTHETIC DEMO", description="Transparency disclaimer: SYNTHETIC DEMO / REAL / MIXED")
    baseline_model_name: str = "Deterministic Rule-Based Crowd Engine V2"
    overall_mae: float
    overall_rmse: float
    directional_accuracy: float
    split_metrics: List[ChronologicalSplitMetrics]
    error_by_destination: List[DestinationErrorMetrics]
    error_by_season: List[SeasonErrorMetrics]
    data_sufficiency_verdict: DataSufficiencyVerdict
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
