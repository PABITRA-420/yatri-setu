from typing import List, Optional
from pydantic import BaseModel

class Experience(BaseModel):
    id: str
    title: str
    description: str
    host_id: str
    host_name: str
    destination_id: str
    destination_name: str
    village: str
    panchayat_name: str
    duration_hours: float
    price_inr: int
    capacity: int
    languages: List[str]
    sustainability_score: int # 0-100
    verification_status: str # "VERIFIED", "UNDER_REVIEW", "PUBLISHED", "REJECTED"
    category: str # "Agri-Tourism", "Forest & Wildlife", "Artisan & Craft", "Culinary & Foraging", "Spiritual Heritage"
    image_url: str
    highlights: List[str] = []
    gear_provided: List[str] = []

class ExperienceCreateRequest(BaseModel):
    title: str
    description: str
    host_id: str
    destination_id: str
    duration_hours: float
    price_inr: int
    capacity: int
    languages: List[str]
    category: str
    image_url: Optional[str] = None
    highlights: Optional[List[str]] = []
