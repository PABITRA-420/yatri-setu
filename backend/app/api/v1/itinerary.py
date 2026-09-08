from fastapi import APIRouter
from app.models.itinerary import (
    ItineraryRequest,
    ItineraryResponse,
    ItineraryOptimizeRequest
)
from app.services.itinerary_service import (
    generate_smart_itinerary_async,
    optimize_smart_itinerary_async
)

router = APIRouter(prefix="/itinerary", tags=["Adaptive AI Itinerary Planner"])

@router.post("/generate", response_model=ItineraryResponse)
async def generate_itinerary(request: ItineraryRequest):
    """
    Generates a crowd-aware, weather-adapted, sustainable multi-day itinerary.
    Uses AI provider abstraction with zero-credential mock fallback.
    """
    return await generate_smart_itinerary_async(request)

@router.post("/optimize", response_model=ItineraryResponse)
async def optimize_itinerary(request: ItineraryOptimizeRequest):
    """
    Adapts an existing itinerary to directives such as:
    MAKE_CHEAPER, MORE_RELAXED, MORE_NATURE, MORE_CULTURE, RAIN_SAFE, FAMILY_FRIENDLY, AVOID_CROWDS, or CUSTOM.
    Keeps crowd, pricing, availability and safety strictly deterministic.
    """
    return await optimize_smart_itinerary_async(request)
