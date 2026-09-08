from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.experience import Experience, ExperienceCreateRequest
from app.services.experience_service import experience_service

router = APIRouter(prefix="/experiences", tags=["Local Experiences"])

@router.get("", response_model=List[Experience])
def list_experiences(
    destination_id: Optional[str] = Query(None, description="Filter by destination id, e.g., 'kalimpong'"),
    verified_only: bool = Query(True, description="Only show verified/published experiences to tourists")
):
    """
    Returns authentic local experiences conducted by verified village hosts and indigenous guides.
    """
    return experience_service.list_experiences(
        destination_id=destination_id,
        verified_only=verified_only
    )

@router.get("/{experience_id}", response_model=Experience)
def get_experience_details(experience_id: str):
    exp = experience_service.get_experience_by_id(experience_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp

@router.post("", response_model=Experience)
def create_experience(req: ExperienceCreateRequest):
    """
    Allows a host or local guide to register a new rural immersive experience.
    """
    return experience_service.create_experience(req)
