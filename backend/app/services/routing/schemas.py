"""
Routing Schemas for Yatri Setu (Milestone 8A).
Normalizes routing metrics, road distance, duration, and GeoJSON geometry.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class RouteGeometry(BaseModel):
    type: str = "LineString"
    coordinates: List[List[float]] = Field(
        ...,
        description="List of [longitude, latitude] coordinate pairs along the road route"
    )


class RouteCalculationResponse(BaseModel):
    origin_destination_id: str
    origin_name: str
    destination_destination_id: str
    destination_name: str
    distance_km: float = Field(..., description="Road travel distance or straight-line estimate in kilometers")
    duration_minutes: int = Field(..., description="Estimated travel time in minutes")
    route_geometry: RouteGeometry = Field(..., description="GeoJSON LineString route path")
    provider: str = Field(..., description="Routing provider identifier: 'osrm', 'demo', or 'fallback'")
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    provenance_label: str = Field(..., description="Provenance tag, e.g., 'REAL — OSRM (OPENSTREETMAP)'")
    is_road_distance: bool = Field(True, description="True if based on actual road network, False if Haversine fallback")
    transit_mode: Optional[str] = "Shared Himalayan Jeep"
    road_condition: Optional[str] = "Mountain highway with winding bends"
    elevation_gain_m: Optional[int] = 0
    carbon_emissions_kg: Optional[float] = 1.2
    traffic_condition: Optional[str] = None
    notes: Optional[str] = None
