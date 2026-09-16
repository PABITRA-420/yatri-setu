from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from app.data.seed_data import DESTINATIONS_DATA
from app.models.destination import Destination, DestinationSummary
from app.models.crowd import (
    CrowdResponse, AlternativesResponse, DateAlternativesResponse, DestinationDecisionResponse
)
from app.services.crowd_engine import calculate_crowd_score
from app.services.alternative_engine import get_alternative_destinations
from app.services.date_advisor import get_date_alternatives
from app.services.flow_decision_engine import compute_destination_decision
from app.services.weather_service import get_destination_weather, WeatherForecast
from app.services.demand_aggregation_service import demand_aggregation_service
from app.models.demand import DemandEventType
from app.services.weather.service import weather_service
from app.services.weather.schemas import WeatherObservation
from app.services.traffic.service import traffic_service
from app.services.traffic.schemas import DestinationTrafficSummary
from app.services.pressure_refresh_service import (
    pressure_refresh_service,
    DestinationLiveConditions,
    PressureExplanation
)

router = APIRouter(prefix="/destinations", tags=["Destinations & Crowd Advisor"])

class DecisionRequest(BaseModel):
    start_date: Optional[str] = "2026-12-25"
    end_date: Optional[str] = "2026-12-27"
    budget: Optional[str] = "Moderate"
    interests: Optional[List[str]] = None
    group_size: Optional[int] = 2

@router.get("", response_model=List[DestinationSummary])
def list_destinations(
    query: Optional[str] = Query(None, description="Search term for destination name or state"),
    crowd_level: Optional[str] = Query(None, description="Filter by crowd level: LOW, MEDIUM, HIGH, VERY HIGH")
):
    """Lists all destinations with crowd score and summary metrics."""
    summaries: List[DestinationSummary] = []
    
    for d in DESTINATIONS_DATA:
        # Search filter
        if query:
            q = query.lower().strip()
            name_match = q in d["name"].lower()
            tag_match = any(q in t.lower() for t in d["tags"])
            state_match = q in d["state"].lower()
            desc_match = q in d["description"].lower()
            if not (name_match or tag_match or state_match or desc_match):
                continue

        crowd = calculate_crowd_score(d["id"])
        
        # Crowd level filter
        if crowd_level and crowd.crowd_level.value.upper() != crowd_level.upper():
            continue

        summaries.append(
            DestinationSummary(
                id=d["id"],
                name=d["name"],
                tagline=d["tagline"],
                region=d["region"],
                state=d["state"],
                hero_image=d["hero_image"],
                crowd_score=crowd.crowd_score,
                crowd_level=crowd.crowd_level.value,
                avg_cost_per_day_inr=d["attributes"]["avg_cost_per_day_inr"],
                tags=d["tags"]
            )
        )
    # Record a single search event per meaningful query
    if query:
        cleaned_query = query.strip()
        if cleaned_query:
            demand_aggregation_service.record_event(
                event_type=DemandEventType.SEARCH.value,
                destination_id=None,
                metadata={"query": cleaned_query}
            )
    return summaries

@router.get("/{destination_id}", response_model=Destination)
def get_destination_details(destination_id: str):
    """Returns complete details, attractions, coordinates, and attributes for a destination."""
    norm_id = destination_id.lower().strip()
    for d in DESTINATIONS_DATA:
        if d["id"] == norm_id:
            try:
                demand_aggregation_service.record_event(
                    event_type=DemandEventType.DESTINATION_SELECTION.value,
                    destination_id=norm_id,
                    metadata={"action": "view_details"}
                )
            except Exception:
                pass
            return Destination(**d)
    raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")

@router.get("/{destination_id}/crowd", response_model=CrowdResponse)
def get_destination_crowd(destination_id: str):
    """Calculates deterministic crowd score (0-100), classification, and explainability factor breakdown."""
    norm_id = destination_id.lower().strip()
    exists = any(d["id"] == norm_id for d in DESTINATIONS_DATA)
    if not exists:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    return calculate_crowd_score(norm_id)

@router.get("/{destination_id}/alternatives", response_model=AlternativesResponse)
def get_destination_alternatives(destination_id: str):
    """Recommends alternative rural/hyperlocal destinations with similarity %, crowd reduction, and cost savings."""
    norm_id = destination_id.lower().strip()
    exists = any(d["id"] == norm_id for d in DESTINATIONS_DATA)
    if not exists:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    return get_alternative_destinations(norm_id)

@router.get("/{destination_id}/date-alternatives", response_model=DateAlternativesResponse)
def get_destination_date_alternatives(
    destination_id: str,
    preferred_start_date: str = Query(..., description="Start date in YYYY-MM-DD format (e.g. 2026-12-25)"),
    preferred_end_date: str = Query(..., description="End date in YYYY-MM-DD format (e.g. 2026-12-27)")
):
    """
    Generates 3 non-overlapping calm travel date windows for the destination with crowd reduction & cost metrics.
    """
    try:
        return get_date_alternatives(destination_id, preferred_start_date, preferred_end_date)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


from app.services.availability.service import availability_service
from app.services.availability.schemas import DestinationAvailabilitySnapshot

@router.get("/{destination_id}/availability", response_model=DestinationAvailabilitySnapshot)
def get_destination_availability(
    destination_id: str,
    date: Optional[str] = Query(None, description="Target date in YYYY-MM-DD format (defaults to today)")
):
    """Returns date-aware accommodation availability snapshot across all verified active properties."""
    norm_id = destination_id.lower().strip()
    exists = any(d["id"] == norm_id for d in DESTINATIONS_DATA)
    if not exists:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    return availability_service.get_destination_availability(norm_id, target_date=date)

@router.get("/{destination_id}/decision", response_model=DestinationDecisionResponse)
def get_destination_flow_decision(
    destination_id: str,
    start_date: Optional[str] = Query("2026-12-25", description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query("2026-12-27", description="End date YYYY-MM-DD"),
    budget: Optional[str] = Query("Moderate", description="Budget level"),
    group_size: Optional[int] = Query(2, description="Number of travelers")
):
    """
    Evaluates crowd pressure and returns flow action (KEEP_DESTINATION, CHANGE_DATES, or CHANGE_DESTINATION)
    along with geographical and temporal alternatives.
    """
    try:
        return compute_destination_decision(
            destination_id=destination_id,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            group_size=group_size or 2
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.post("/{destination_id}/decision", response_model=DestinationDecisionResponse)
def post_destination_flow_decision(
    destination_id: str,
    body: DecisionRequest = Body(default_factory=DecisionRequest)
):
    """POST variant for flow decision engine with structured preferences."""
    try:
        decision = compute_destination_decision(
            destination_id=destination_id,
            start_date=body.start_date,
            end_date=body.end_date,
            budget=body.budget,
            interests=body.interests,
            group_size=body.group_size or 2
        )
        return decision
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

class AlternativeAcceptanceRequest(BaseModel):
    origin_destination_id: Optional[str] = None
    original_destination_id: Optional[str] = None
    alternative_destination_id: str
    similarity_score: Optional[int] = None
    session_id: Optional[str] = None

@router.post("/{destination_id}/accept-alternative")
def accept_alternative_destination(
    destination_id: str,
    body: AlternativeAcceptanceRequest = Body(...)
):
    """
    Explicitly records an AlternativeAcceptanceEvent when a tourist clicks/chooses an alternative destination.
    """
    orig_id = body.original_destination_id or body.origin_destination_id or destination_id
    alt_id = body.alternative_destination_id.lower().strip()

    event = demand_aggregation_service.record_event(
        event_type=DemandEventType.ALTERNATIVE_ACCEPTANCE.value,
        destination_id=alt_id,
        session_id=body.session_id,
        metadata={
            "original_destination_id": orig_id.lower().strip(),
            "origin_destination_id": orig_id.lower().strip(),
            "alternative_destination_id": alt_id,
            "similarity_score": body.similarity_score
        }
    )
    return {
        "status": event.get("status", "recorded"),
        "event_id": event["id"],
        "original_destination_id": orig_id,
        "alternative_destination_id": alt_id
    }

@router.get("/{destination_id}/weather", response_model=WeatherForecast)
def get_weather_forecast(destination_id: str):
    """Returns real-time or simulated Himalayan mountain weather forecast for the destination."""
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    if destination_id.lower().strip() not in dest_map:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    return get_destination_weather(destination_id)

@router.get("/circuit/conditions")
def get_circuit_conditions():
    """Returns live weather, traffic, and recalculated pressure across all circuit destinations."""
    return pressure_refresh_service.refresh_all_destinations()

@router.get("/{destination_id}/live-weather", response_model=WeatherObservation)
def get_destination_live_weather(destination_id: str):
    """Returns normalized live weather observation with strict provenance and cache status."""
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    if destination_id.lower().strip() not in dest_map:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    return weather_service.get_weather(destination_id)

@router.get("/{destination_id}/traffic", response_model=DestinationTrafficSummary)
def get_destination_traffic(destination_id: str):
    """Returns multi-route arterial road telemetry and access status (OPEN, CAUTION, DISRUPTED)."""
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    if destination_id.lower().strip() not in dest_map:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    return traffic_service.get_traffic(destination_id)

@router.get("/{destination_id}/live-pressure")
def get_destination_live_pressure(
    destination_id: str,
    target_date: Optional[str] = Query(None, description="Optional target date YYYY-MM-DD")
):
    """Returns dynamically recalculated pressure incorporating live weather, traffic, demand, and events."""
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    if destination_id.lower().strip() not in dest_map:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    return pressure_refresh_service.recalculate_destination_pressure(destination_id, target_date_str=target_date)

@router.get("/{destination_id}/pressure-explanation", response_model=PressureExplanation)
def get_destination_pressure_explanation(
    destination_id: str,
    target_date: Optional[str] = Query(None, description="Optional target date YYYY-MM-DD")
):
    """Returns deterministic human-readable explanation of top pressure drivers and access status."""
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    if destination_id.lower().strip() not in dest_map:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    cond = pressure_refresh_service.recalculate_destination_pressure(destination_id, target_date_str=target_date)
    return PressureExplanation(
        destination_id=cond.destination_id,
        pressure_level=cond.pressure_level,
        pressure_score=cond.pressure_score,
        top_drivers=cond.top_drivers,
        access_status=cond.access_status,
        generated_at=cond.refreshed_at
    )

@router.get("/{destination_id}/conditions", response_model=DestinationLiveConditions)
def get_destination_conditions(
    destination_id: str,
    target_date: Optional[str] = Query(None, description="Optional target date YYYY-MM-DD for forecast conditions")
):
    """Comprehensive conditions endpoint: weather, traffic, access status, pressure, and top drivers."""
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    if destination_id.lower().strip() not in dest_map:
        raise HTTPException(status_code=404, detail=f"Destination '{destination_id}' not found")
    return pressure_refresh_service.recalculate_destination_pressure(destination_id, target_date_str=target_date)

