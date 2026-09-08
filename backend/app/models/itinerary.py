"""
Itinerary Models for Yatri Setu (Smart India Hackathon 2026)
Defines itinerary requests, responses, AI context, and optimization payloads.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from app.services.weather_service import WeatherForecast
from app.services.sustainability_engine import TourismImpact, SustainabilityScorecard
from app.services.route_service import RouteSegment

class ActivitySlot(BaseModel):
    time_slot: str # e.g. "08:30 AM - 10:30 AM"
    period: str # "Morning", "Afternoon", "Evening"
    title: str
    description: str
    location_name: str
    crowd_forecast: str # "Low", "Moderate", "High"
    cost_estimate_inr: int
    duration_hrs: float
    travel_tip: Optional[str] = None
    category: str # "Culture", "Nature", "Culinary", "Scenic", "Indoor"
    image_url: Optional[str] = None
    is_weather_adapted: bool = False
    adaptation_reason: Optional[str] = None

class ItineraryDay(BaseModel):
    day_number: int
    theme: str
    overview: str
    estimated_budget_inr: int
    activities: List[ActivitySlot]
    transit_advice: str

class ItineraryRequest(BaseModel):
    destination_id: str
    duration_days: int = Field(3, ge=1, le=5)
    traveler_type: str = Field("Solo", description="Solo, Couple, Family, Friends")
    pace: str = Field("Moderate", description="Relaxed, Moderate, Active")
    interests: List[str] = Field(default_factory=lambda: ["Nature", "Culture", "Local Food"])
    budget_level: str = Field("Moderate", description="Budget, Moderate, Premium")
    start_date: Optional[str] = None
    optimize_for_weather: bool = True

class ItineraryResponse(BaseModel):
    itinerary_id: str
    destination_id: str
    destination_name: str
    duration_days: int
    traveler_type: str
    pace: str
    interests: List[str]
    total_estimated_budget_inr: int
    crowd_avoidance_rating: str # e.g. "92% Overcrowding Avoided"
    local_economic_impact_tag: str
    days: List[ItineraryDay]
    ai_generated_note: str

    # Milestone 2B Enhanced Intelligence
    sustainability_score: int = 88
    sustainability_classification: str = "EXCELLENT"
    tourism_impact: Optional[TourismImpact] = None
    weather_forecast: Optional[WeatherForecast] = None
    weather_adaptation_notice: Optional[str] = None
    why_this_itinerary: List[str] = Field(default_factory=list)
    ai_provider_used: str = "mock"
    optimization_history: List[str] = Field(default_factory=list)

class ItineraryOptimizeRequest(BaseModel):
    itinerary_id: str
    destination_id: str
    instruction: str # "MAKE_CHEAPER", "MORE_RELAXED", "MORE_NATURE", "MORE_CULTURE", "RAIN_SAFE", "FAMILY_FRIENDLY", "AVOID_CROWDS", "CUSTOM"
    custom_instruction: Optional[str] = None
    current_itinerary: Optional[ItineraryResponse] = None

class ItineraryContext(BaseModel):
    destination_id: str
    destination_name: str
    crowd_score: int
    crowd_classification: str
    weather: WeatherForecast
    attractions: List[Dict[str, Any]]
    route_estimates: List[RouteSegment]
    user_preferences: Dict[str, Any]
    optimization_goal: Optional[str] = None
    custom_instruction: Optional[str] = None

# Structured AI validation schema
class AIActivityOutput(BaseModel):
    time_slot: str
    period: str
    title: str
    description: str
    location_name: str
    crowd_forecast: str
    cost_estimate_inr: int
    duration_hrs: float
    travel_tip: Optional[str] = None
    category: str
    is_weather_adapted: bool = False
    adaptation_reason: Optional[str] = None

class AIDayOutput(BaseModel):
    day_number: int
    theme: str
    overview: str
    activities: List[AIActivityOutput]
    transit_advice: str

class AIItineraryOutput(BaseModel):
    overview_note: str
    why_this_itinerary: List[str]
    weather_adaptation_notice: Optional[str] = None
    days: List[AIDayOutput]
