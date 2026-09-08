from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Coordinates(BaseModel):
    lat: float
    lng: float

class Attraction(BaseModel):
    id: str
    name: str
    category: str
    description: str
    crowd_density: str # Low, Medium, High
    visit_duration_hrs: float
    best_time: str
    image_url: str

class DestinationAttributes(BaseModel):
    nature: float = Field(..., ge=0, le=10, description="Score 0-10 for nature appeal")
    climate: str = Field(..., description="E.g. Alpine, Sub-tropical, Temperate")
    activities: List[str]
    culture: str
    budget_level: str # Budget, Moderate, Premium
    avg_cost_per_day_inr: int
    accessibility: str
    altitude_ft: int

class Destination(BaseModel):
    id: str
    name: str
    tagline: str
    region: str
    state: str
    description: str
    coordinates: Coordinates
    hero_image: str
    gallery_images: List[str]
    attributes: DestinationAttributes
    highlights: List[str]
    attractions: List[Attraction]
    base_crowd_score: int
    recommended_duration_days: int
    tags: List[str]

class DestinationSummary(BaseModel):
    id: str
    name: str
    tagline: str
    region: str
    state: str
    hero_image: str
    crowd_score: int
    crowd_level: str
    avg_cost_per_day_inr: int
    tags: List[str]
    distance_from_query_km: Optional[float] = None
