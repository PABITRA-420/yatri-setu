"""
Weather Schemas for Yatri Setu (Milestone 7C).
Defines normalized weather observations, forecasts, impact signals, and cache status models.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class WeatherObservation(BaseModel):
    """Normalized weather observation for a destination with strict provenance."""
    destination_id: str
    destination_name: str
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    forecast_for: Optional[str] = None  # YYYY-MM-DD for forecast, None for current
    temperature_c: float
    temp_min_c: float
    temp_max_c: float
    precipitation_probability: int = Field(..., ge=0, le=100)
    precipitation_mm: float = Field(default=0.0, ge=0.0)
    humidity: int = Field(..., ge=0, le=100)
    wind_speed_kmh: float = Field(default=10.0, ge=0.0)
    weather_condition: str
    severe_weather: Optional[str] = None
    visibility_km: float = Field(default=10.0, ge=0.0)
    advisory: str
    best_hours_for_outdoors: Optional[str] = None
    source: str
    provider_mode: str  # REAL, DEMO, UNAVAILABLE
    provenance_label: str = "DEMO MODE — SYNTHETIC DATA"  # REAL — EXTERNAL PROVIDER, DEMO MODE — SYNTHETIC DATA, etc.
    confidence: float = Field(..., ge=0.0, le=1.0)
    data_quality: str  # HIGH, MEDIUM, DEGRADED, UNKNOWN
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    cache_status: str = "LIVE"  # LIVE, CACHED, STALE, UNAVAILABLE
    expires_at: Optional[datetime] = None


class WeatherImpactSignal(BaseModel):
    """
    Deterministic weather impact calculation.
    Weather impact score ∈ [-1.0, +1.0]:
      - Near 0 to +0.2: Pleasant weather (modest positive demand effect)
      - -0.1 to -0.4: Moderate rain / mist (slight outdoor dampening)
      - -0.5 to -0.8: Heavy rain / monsoon (substantial outdoor reduction)
      - -1.0: Severe storm / landslide warning (safety advisory override)
    """
    destination_id: str
    weather_impact: float = Field(..., ge=-1.0, le=1.0)
    impact_factor: float = Field(..., ge=0.0, le=100.0)  # 0-100 scale for composite normalization
    advisory_level: str = "NORMAL"  # NORMAL, ADVISORY, WARNING, CRITICAL
    tourism_suitability: str = "GOOD"  # EXCELLENT, GOOD, MODERATE, POOR, HAZARDOUS
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str
    provider_mode: str
    provenance_label: str = "DEMO MODE — SYNTHETIC DATA"
    observed_at: datetime = Field(default_factory=datetime.utcnow)
