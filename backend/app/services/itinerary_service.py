"""
Itinerary Service for Yatri Setu (Smart India Hackathon 2026)
Orchestrates AI providers, deterministic crowd scoring, meteorological intelligence,
route transit estimates, and village sustainability metrics.
"""

import uuid
import asyncio
import concurrent.futures
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

VALID_CROWD_FORECAST_VALUES = {"Low", "Moderate", "High", "Very High"}
ACTIVITY_COST_MIN_INR = 50
ACTIVITY_COST_MAX_INR = 5000


def _validate_ai_output(ai_output, context) -> None:
    """
    Post-generation validation guard against LLM hallucination.
    Checks for unrealistic costs, activity counts, and invalid crowd forecast values.
    Sanitizes in-place and logs AI_HALLUCINATION_RISK warnings.
    """
    for day in (ai_output.days or []):
        # Activity count check
        if len(day.activities) < 2 or len(day.activities) > 5:
            logger.warning(
                f"AI_HALLUCINATION_RISK: Day {day.day_number} has {len(day.activities)} activities "
                f"(expected 2-5) for dest='{context.destination_id}'"
            )

        for act in day.activities:
            # Cost sanity check
            if not (ACTIVITY_COST_MIN_INR <= act.cost_estimate_inr <= ACTIVITY_COST_MAX_INR):
                logger.warning(
                    f"AI_HALLUCINATION_RISK: Activity '{act.title}' has cost {act.cost_estimate_inr} INR "
                    f"outside allowed range [{ACTIVITY_COST_MIN_INR}, {ACTIVITY_COST_MAX_INR}]. Clamping."
                )
                act.cost_estimate_inr = max(ACTIVITY_COST_MIN_INR, min(ACTIVITY_COST_MAX_INR, act.cost_estimate_inr))

            # Period normalization check
            if act.period:
                p_lower = act.period.lower()
                if "morn" in p_lower:
                    act.period = "Morning"
                elif "after" in p_lower or "noon" in p_lower or "lunch" in p_lower:
                    act.period = "Afternoon"
                elif "even" in p_lower or "night" in p_lower or "dinner" in p_lower:
                    act.period = "Evening"
                else:
                    act.period = act.period.capitalize()
            else:
                act.period = "Morning"

            # Weather adaptation reason standardization
            if act.is_weather_adapted:
                if not act.adaptation_reason or "Yatri Setu adapted" not in act.adaptation_reason:
                    prefix = "Yatri Setu adapted this activity because of expected mountain rain"
                    if act.adaptation_reason:
                        act.adaptation_reason = f"{prefix}: {act.adaptation_reason}"
                    else:
                        act.adaptation_reason = f"{prefix}."

            # Crowd forecast value check
            if act.crowd_forecast not in VALID_CROWD_FORECAST_VALUES:
                logger.warning(
                    f"AI_HALLUCINATION_RISK: Activity '{act.title}' has invalid crowd_forecast='{act.crowd_forecast}'. "
                    f"Normalizing to context score."
                )
                score = context.crowd_score
                act.crowd_forecast = (
                    "Low" if score <= 25 else
                    "Moderate" if score <= 50 else
                    "High" if score <= 75 else
                    "Very High"
                )

from app.models.itinerary import (
    ItineraryRequest,
    ItineraryResponse,
    ItineraryOptimizeRequest,
    ItineraryDay,
    ActivitySlot,
    ItineraryContext,
    AIItineraryOutput
)
from app.data.seed_data import DESTINATIONS_DATA
from app.services.crowd_engine import calculate_crowd_score
from app.services.weather_service import get_destination_weather
from app.services.route_service import get_route_estimate
from app.services.sustainability_engine import calculate_sustainability
from app.services.ai import get_ai_provider

CATEGORY_IMAGES: Dict[str, str] = {
    "Culture": "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=600&q=80",
    "Nature": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=600&q=80",
    "Culinary": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=600&q=80",
    "Scenic": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80",
    "Indoor": "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?auto=format&fit=crop&w=600&q=80",
    "Agri-Tourism": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80"
}

def _run_async_safely(coro):
    """Executes an async coroutine safely in both sync and async environments."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)

def _build_context(
    destination_id: str,
    user_preferences: Dict[str, Any],
    optimization_goal: Optional[str] = None,
    custom_instruction: Optional[str] = None
) -> ItineraryContext:
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    norm_id = destination_id.lower().strip()
    dest = dest_map.get(norm_id, dest_map["kalimpong"])

    crowd_resp = calculate_crowd_score(dest["id"])
    weather = get_destination_weather(dest["id"])
    
    # Inter-town and local routes
    routes = [
        get_route_estimate(dest["id"], dest["id"]),
        get_route_estimate("darjeeling", dest["id"]) if dest["id"] != "darjeeling" else get_route_estimate("darjeeling", "kalimpong")
    ]

    return ItineraryContext(
        destination_id=dest["id"],
        destination_name=dest["name"],
        crowd_score=crowd_resp.crowd_score,
        crowd_classification=crowd_resp.crowd_level.value,
        weather=weather,
        attractions=dest.get("attractions", []),
        route_estimates=routes,
        user_preferences=user_preferences,
        optimization_goal=optimization_goal,
        custom_instruction=custom_instruction
    )

def _convert_ai_output_to_response(
    ai_output: AIItineraryOutput,
    context: ItineraryContext,
    itinerary_id: Optional[str] = None,
    optimization_history: Optional[List[str]] = None,
    provider_name: str = "mock"
) -> ItineraryResponse:
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    dest = dest_map.get(context.destination_id, dest_map["kalimpong"])
    
    days: List[ItineraryDay] = []
    total_budget = 0

    for d_idx, day_out in enumerate(ai_output.days):
        act_slots: List[ActivitySlot] = []
        day_cost = 0

        for a_idx, a_out in enumerate(day_out.activities):
            day_cost += a_out.cost_estimate_inr
            # Pick contextual image
            img_url = CATEGORY_IMAGES.get(a_out.category, dest["hero_image"])
            if a_idx == 0 and dest.get("hero_image"):
                img_url = dest["hero_image"]
            elif a_idx == 1 and dest.get("gallery_images") and len(dest["gallery_images"]) > 0:
                img_url = dest["gallery_images"][0]

            act_slots.append(ActivitySlot(
                time_slot=a_out.time_slot,
                period=a_out.period,
                title=a_out.title,
                description=a_out.description,
                location_name=a_out.location_name,
                crowd_forecast=a_out.crowd_forecast,
                cost_estimate_inr=a_out.cost_estimate_inr,
                duration_hrs=a_out.duration_hrs,
                travel_tip=a_out.travel_tip,
                category=a_out.category,
                image_url=img_url,
                is_weather_adapted=a_out.is_weather_adapted,
                adaptation_reason=a_out.adaptation_reason
            ))

        total_budget += day_cost
        days.append(ItineraryDay(
            day_number=day_out.day_number,
            theme=day_out.theme,
            overview=day_out.overview,
            estimated_budget_inr=day_cost,
            activities=act_slots,
            transit_advice=day_out.transit_advice
        ))

    duration = len(days) or context.user_preferences.get("duration_days", 3)
    scorecard = calculate_sustainability(
        destination_id=context.destination_id,
        total_budget_inr=max(1200 * duration, total_budget),
        crowd_score=context.crowd_score,
        num_days=duration,
        prefers_shared_transit=True,
        homestay_selected=True
    )

    crowd_avoidance = f"{max(75, 100 - context.crowd_score)}% Overcrowding Avoided" if context.crowd_score < 70 else "Off-Peak Time Sequencing Applied"
    
    return ItineraryResponse(
        itinerary_id=itinerary_id or f"itin-{uuid.uuid4().hex[:8]}",
        destination_id=context.destination_id,
        destination_name=context.destination_name,
        duration_days=duration,
        traveler_type=context.user_preferences.get("traveler_type", "Solo"),
        pace=context.user_preferences.get("pace", "Moderate"),
        interests=context.user_preferences.get("interests", ["Nature", "Culture", "Local Food"]),
        total_estimated_budget_inr=total_budget,
        crowd_avoidance_rating=crowd_avoidance,
        local_economic_impact_tag=f"🌱 {scorecard.tourism_impact.direct_village_economy_percent}% Direct Village Retention",
        days=days,
        ai_generated_note=ai_output.overview_note,
        sustainability_score=scorecard.sustainability_score,
        sustainability_classification=scorecard.sustainability_classification,
        tourism_impact=scorecard.tourism_impact,
        weather_forecast=context.weather,
        weather_adaptation_notice=ai_output.weather_adaptation_notice,
        why_this_itinerary=ai_output.why_this_itinerary,
        ai_provider_used=ai_output.provider_used or provider_name,
        optimization_history=optimization_history or []
    )

async def generate_smart_itinerary_async(
    req: ItineraryRequest,
    provider_override: Optional[str] = None
) -> ItineraryResponse:
    """Async generator orchestrating AI provider, crowd, weather, and sustainability."""
    user_prefs = {
        "duration_days": min(5, max(1, req.duration_days)),
        "traveler_type": req.traveler_type,
        "pace": req.pace,
        "interests": req.interests,
        "budget_level": req.budget_level,
        "start_date": req.start_date
    }
    context = _build_context(req.destination_id, user_prefs)
    provider = get_ai_provider(provider_override)
    ai_output = await provider.generate_itinerary(context)
    _validate_ai_output(ai_output, context)
    
    return _convert_ai_output_to_response(
        ai_output=ai_output,
        context=context,
        provider_name=provider.provider_name
    )

def generate_smart_itinerary(req: ItineraryRequest) -> ItineraryResponse:
    """Synchronous entrypoint for backward compatibility and simple endpoint handlers."""
    return _run_async_safely(generate_smart_itinerary_async(req))

async def optimize_smart_itinerary_async(
    req: ItineraryOptimizeRequest,
    provider_override: Optional[str] = None
) -> ItineraryResponse:
    """Async optimizer applying adaptive travel directives to existing itinerary."""
    dest_id = req.destination_id
    user_prefs = {
        "duration_days": 3,
        "traveler_type": "Solo",
        "pace": "Moderate",
        "interests": ["Nature", "Culture", "Local Food"],
        "budget_level": "Moderate"
    }
    history = []
    
    if req.current_itinerary:
        curr = req.current_itinerary
        dest_id = curr.destination_id
        user_prefs["duration_days"] = curr.duration_days
        user_prefs["traveler_type"] = curr.traveler_type
        user_prefs["pace"] = curr.pace
        user_prefs["interests"] = curr.interests
        history = list(curr.optimization_history)
        current_dict = curr.model_dump()
    else:
        current_dict = {}

    context = _build_context(
        destination_id=dest_id,
        user_preferences=user_prefs,
        optimization_goal=req.instruction,
        custom_instruction=req.custom_instruction
    )
    
    provider = get_ai_provider(provider_override)
    ai_output = await provider.optimize_itinerary(
        context=context,
        current_itinerary=current_dict,
        instruction=req.instruction,
        custom_instruction=req.custom_instruction
    )
    _validate_ai_output(ai_output, context)

    used_name = ai_output.provider_used or provider.provider_name
    history.append(f"Directive '{req.instruction}' applied via {used_name}")

    return _convert_ai_output_to_response(
        ai_output=ai_output,
        context=context,
        itinerary_id=req.itinerary_id,
        optimization_history=history,
        provider_name=used_name
    )

def optimize_smart_itinerary(req: ItineraryOptimizeRequest) -> ItineraryResponse:
    """Synchronous optimizer wrapper."""
    return _run_async_safely(optimize_smart_itinerary_async(req))
