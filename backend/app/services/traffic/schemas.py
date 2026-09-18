"""
Traffic Schemas for Yatri Setu (Milestone 7C).
Defines route-level telemetry, destination-level summaries, and traffic impact signals.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class RouteTrafficObservation(BaseModel):
    """Corridor-specific mountain road telemetry observation."""
    route_id: str
    route_name: str
    origin: str
    destination_id: str
    current_travel_time_min: int = Field(..., ge=1)
    historical_travel_time_min: int = Field(..., ge=1)
    travel_time_ratio: float = Field(..., ge=0.5)
    travel_time_anomaly_percent: float
    congestion_level: str  # NORMAL, ELEVATED, HIGH, CRITICAL
    road_status: str  # CLEAR, SLOW, RESTRICTED, CLOSED
    incident_count: int = Field(default=0, ge=0)
    incident_description: Optional[str] = None


class DestinationTrafficSummary(BaseModel):
    """
    Multi-route destination arterial traffic summary.
    Separates route accessibility (OPEN, CAUTION, DISRUPTED) from crowd pressure.
    """
    destination_id: str
    destination_name: str
    overall_congestion_score: float = Field(..., ge=0.0, le=100.0)
    average_travel_time_ratio: float = Field(..., ge=0.5)
    travel_time_anomaly_percent: float
    incident_count: int = Field(default=0, ge=0)
    access_status: str = "OPEN"  # OPEN, CAUTION, DISRUPTED, UNKNOWN
    primary_bottleneck_route: Optional[str] = None
    critical_routes: List[RouteTrafficObservation]
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    source: str
    provider_mode: str  # REAL, DEMO, UNAVAILABLE
    confidence: float = Field(..., ge=0.0, le=1.0)
    data_quality: str  # HIGH, MEDIUM, DEGRADED, UNKNOWN
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    cache_status: str = "LIVE"  # LIVE, CACHED, STALE, UNAVAILABLE
    provenance_label: Optional[str] = "DEMO MODE — SYNTHETIC DATA"
    expires_at: Optional[datetime] = None


class TrafficImpactSignal(BaseModel):
    """
    Deterministic traffic impact signal for destination pressure aggregation.
    """
    destination_id: str
    traffic_impact_score: float = Field(..., ge=0.0, le=100.0)
    traffic_status: str  # NORMAL, ELEVATED, HIGH, CRITICAL
    travel_time_anomaly_percent: float
    access_status: str  # OPEN, CAUTION, DISRUPTED, UNKNOWN
    bottleneck_corridor: Optional[str] = None
    impact_description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str
    provider_mode: str
    observed_at: datetime = Field(default_factory=datetime.utcnow)
