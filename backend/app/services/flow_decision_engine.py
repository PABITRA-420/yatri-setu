from typing import List, Optional
from app.models.crowd import DestinationDecisionResponse, CrowdLevel
from app.services.crowd_engine import calculate_crowd_score
from app.services.alternative_engine import get_alternative_destinations
from app.services.date_advisor import get_date_alternatives, calculate_preferred_date_crowd, parse_date
from app.data.seed_data import DESTINATIONS_DATA

def compute_destination_decision(
    destination_id: str,
    start_date: Optional[str] = "2026-12-25",
    end_date: Optional[str] = "2026-12-27",
    budget: Optional[str] = "Moderate",
    interests: Optional[List[str]] = None,
    group_size: int = 2
) -> DestinationDecisionResponse:
    """
    Synthesizes geographical alternatives, temporal date alternatives, and crowd pressure
    to provide an actionable flow management recommendation: KEEP_DESTINATION, CHANGE_DATES, or CHANGE_DESTINATION.
    """
    norm_id = destination_id.lower().strip()
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    if norm_id not in dest_map:
        raise KeyError(f"Destination '{destination_id}' not found")

    dest = dest_map[norm_id]

    # Validate dates or use defaults
    s_date = start_date or "2026-12-25"
    e_date = end_date or "2026-12-27"
    try:
        s_dt = parse_date(s_date)
        e_dt = parse_date(e_date)
        if e_dt <= s_dt:
            s_date, e_date = "2026-12-25", "2026-12-27"
            s_dt = parse_date(s_date)
            e_dt = parse_date(e_date)
    except Exception:
        s_date, e_date = "2026-12-25", "2026-12-27"
        s_dt = parse_date(s_date)
        e_dt = parse_date(e_date)

    # 1. Calculate preferred date crowd score
    crowd_score = calculate_preferred_date_crowd(norm_id, s_dt, e_dt)
    base_crowd = calculate_crowd_score(norm_id)
    crowd_status = base_crowd.crowd_level

    # 2. Get alternative destinations
    alt_dest_res = get_alternative_destinations(norm_id)
    alt_destinations = alt_dest_res.alternatives

    # 3. Get alternative dates
    alt_date_res = get_date_alternatives(norm_id, s_date, e_date)
    alt_dates = alt_date_res.date_alternatives

    # 4. Generate specific alerts
    alerts: List[str] = []
    if crowd_score > 75:
        alerts.append(f"CRITICAL OVERTOURISM: {dest['name']} is operating at {crowd_score}/100 crowd capacity.")
        alerts.append("Narrow arterial highways and viewpoint queues experiencing severe bottlenecks.")
        alerts.append("Homestays in neighboring serene ridges offer immediate availability and lower ecological impact.")
    elif crowd_score > 50:
        alerts.append(f"HIGH DENSITY: Moderate queuing observed at top tourist viewpoints.")
    else:
        alerts.append(f"BALANCED FOOTFALL: {dest['name']} has healthy room availability and smooth transit.")

    # 5. Determine recommended action
    if crowd_score <= 50:
        recommended_action = "KEEP_DESTINATION"
    else:
        # If top alternative has high similarity >= 85% and significantly lower crowd:
        if alt_destinations and alt_destinations[0].similarity_score >= 85 and alt_destinations[0].crowd_score <= 50:
            recommended_action = "CHANGE_DESTINATION"
        else:
            recommended_action = "CHANGE_DATES"

    selected_dates_str = f"{s_date} to {e_date}"

    return DestinationDecisionResponse(
        selected_destination=dest["name"],
        destination_id=norm_id,
        selected_dates=selected_dates_str,
        crowd_status=crowd_status,
        crowd_score=crowd_score,
        alerts=alerts,
        alternative_destinations=alt_destinations,
        alternative_dates=alt_dates,
        recommended_action=recommended_action
    )
