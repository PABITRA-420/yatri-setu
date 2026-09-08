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
    distance_km: float
    estimated_cost_per_day: int
    cost_difference_percent: int # e.g. -35%
    reasons_to_recommend: List[str]
    shared_highlights: List[str]
    matching_attributes: List[str] = Field(default_factory=list)
    key_experience: str
    eco_tag: str

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
