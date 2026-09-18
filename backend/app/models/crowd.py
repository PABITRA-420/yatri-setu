from enum import Enum
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

class CrowdLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY HIGH"

class CrowdFactorItem(BaseModel):
    name: str
    key: str
    raw_value: float = Field(..., ge=0, le=100, description="Normalized raw value 0-100")
    weight_percentage: int
    weighted_contribution: float
    description: str

class CrowdResponse(BaseModel):
    destination_id: str
    destination_name: str
    crowd_score: int = Field(..., ge=0, le=100)
    crowd_level: CrowdLevel
    color_code: str
    summary: str
    why_crowded: List[str]
    bottlenecks: List[str]
    peak_visiting_hours: str
    best_time_to_visit_today: str
    factors: List[CrowdFactorItem]
    live_traffic_status: str
    hotel_occupancy_rate: str
    last_updated: str
    provenance_label: Optional[str] = "REAL — DATABASE & TELEMETRY"
    provider_mode: Optional[str] = "REAL"
    data_quality: Optional[str] = "HIGH" 

class AlternativeWeather(BaseModel):
    """Structured weather observation for alternative destination cards."""
    destination_id: str = Field(..., description="Destination identifier")
    temperature: float = Field(..., description="Current temperature in Celsius")
    temp_min_c: Optional[float] = Field(None, description="Minimum temperature in Celsius")
    temp_max_c: Optional[float] = Field(None, description="Maximum temperature in Celsius")
    condition: str = Field(..., description="Weather condition description")
    humidity: Optional[int] = Field(None, description="Relative humidity percentage")
    precipitation_chance: Optional[int] = Field(None, description="Precipitation probability percentage")
    provenance_label: str = Field("DEMO MODE — SYNTHETIC DATA", description="Explicit weather provenance label")
    provider_mode: str = Field("DEMO", description="Provider mode: REAL, DEMO, UNAVAILABLE")
    cache_status: str = Field("LIVE", description="Cache status: LIVE, CACHED, STALE, DEMO")
    observed_at: Optional[str] = Field(None, description="Observation timestamp")
    temperature_range: Optional[str] = Field(None, description="Formatted temperature range (e.g. 14°C - 22°C)")

class AlternativeRecommendation(BaseModel):
    id: str
    name: str
    tagline: str
    state: str
    hero_image: str
    crowd_score: int
    crowd_level: CrowdLevel
    similarity_score: int = Field(..., ge=0, le=100, description="Percentage match")
    original_crowd_score: int = Field(88, description="Origin destination crowd score")
    alternative_crowd_score: int = Field(42, description="Alternative destination crowd score")
    crowd_reduction_percent: int = Field(..., description="Percentage crowd reduction vs original")
    # Distance fields — clearly distinguished by provenance
    distance_km: float = Field(..., description="Primary distance (road if OSRM available, else geographic)")
    geographic_distance_km: Optional[float] = Field(None, description="Haversine straight-line geographic distance in km")
    road_distance_km: Optional[float] = Field(None, description="OSRM road network distance in km (None if unavailable)")
    distance_provenance: str = Field("HAVERSINE_GEOGRAPHIC_ESTIMATE", description="'OSRM_ROAD_DISTANCE' or 'HAVERSINE_GEOGRAPHIC_ESTIMATE'")
    estimated_cost_per_day: int
    cost_difference_percent: int # e.g. -35%
    reasons_to_recommend: List[str]
    shared_highlights: List[str]
    matching_attributes: List[str] = Field(default_factory=list)
    key_experience: str
    eco_tag: str
    # Milestone 7D Capacity & Network Intelligence
    destination_id: Optional[str] = Field(None, description="Standard destination identifier")
    current_pressure: Optional[int] = Field(None, description="Current crowd/pressure score")
    expected_pressure: Optional[int] = Field(None, description="Expected pressure forecast")
    capacity_status: str = Field("HEALTHY", description="Accommodation capacity health: HEALTHY, LIMITED, FULL")
    available_capacity: Optional[int] = Field(None, description="Available accommodation units (rooms)")
    access_status: str = Field("OPEN", description="Corridor access status: OPEN, CAUTION, DISRUPTED")
    weather: Optional[AlternativeWeather] = Field(None, description="Destination-specific canonical weather observation")
    weather_summary: Optional[str] = Field(None, description="Summary of current mountain weather")
    traffic_summary: Optional[str] = Field(None, description="Summary of connecting corridor traffic")
    homestay_availability: Optional[str] = Field(None, description="Status of authentic homestay inventory")
    reasons: List[str] = Field(default_factory=list, description="Curated explainable reasons for suggestion")
    provenance: str = Field("REAL — YATRI SETU NETWORK", description="Data provenance")
    last_updated: Optional[str] = Field(None, description="ISO timestamp of recommendation calculation")

class AlternativesResponse(BaseModel):
    origin_destination_id: str
    origin_destination_name: str
    origin_crowd_score: int
    origin_crowd_level: CrowdLevel
    alternatives: List[AlternativeRecommendation]

class DateAlternativeRecommendation(BaseModel):
    start_date: str
    end_date: str
    window_label: str
    crowd_score: int
    crowd_classification: CrowdLevel
    crowd_reduction_percent: int
    estimated_cost_change: str
    availability_score: int
    reason: str

class DateAlternativesResponse(BaseModel):
    destination_id: str
    destination_name: str
    preferred_start_date: str
    preferred_end_date: str
    preferred_crowd_score: int
    preferred_crowd_classification: CrowdLevel
    date_alternatives: List[DateAlternativeRecommendation]

class DestinationDecisionResponse(BaseModel):
    selected_destination: str
    destination_id: str
    selected_dates: str
    crowd_status: CrowdLevel
    crowd_score: int
    alerts: List[str]
    alternative_destinations: List[AlternativeRecommendation]
    alternative_dates: List[DateAlternativeRecommendation]
    recommended_action: Literal["KEEP_DESTINATION", "CHANGE_DATES", "CHANGE_DESTINATION"]
