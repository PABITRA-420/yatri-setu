from datetime import datetime, timedelta
from typing import List, Tuple
from app.data.seed_data import DESTINATIONS_DATA
from app.models.crowd import (
    CrowdLevel, DateAlternativeRecommendation, DateAlternativesResponse
)
from app.services.crowd_engine import calculate_crowd_score, classify_crowd_level

def parse_date(date_str: str) -> datetime:
    """Parses YYYY-MM-DD string into datetime."""
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except Exception:
        raise ValueError(f"Invalid date format '{date_str}'. Expected YYYY-MM-DD (e.g. 2026-12-25)")

def format_window_label(start_dt: datetime, end_dt: datetime) -> str:
    """Formats two datetimes into readable label like '5 - 7 Jan' or '28 Oct - 1 Nov'."""
    if start_dt.month == end_dt.month:
        return f"{start_dt.day} - {end_dt.day} {start_dt.strftime('%b')}"
    return f"{start_dt.day} {start_dt.strftime('%b')} - {end_dt.day} {end_dt.strftime('%b')}"

def is_peak_holiday_window(dt: datetime) -> bool:
    """Checks if date falls into peak holiday surges (late Dec / New Year, Dussehra/Diwali, or summer peak)."""
    month = dt.month
    day = dt.day
    # Christmas to New Year peak (Dec 20 - Jan 3)
    if (month == 12 and day >= 20) or (month == 1 and day <= 3):
        return True
    # Durga Puja / Dussehra autumn peak (Oct 10 - Oct 25)
    if month == 10 and 10 <= day <= 25:
        return True
    # May summer vacation surge
    if month == 5 and 10 <= day <= 31:
        return True
    return False

def calculate_preferred_date_crowd(destination_id: str, start_dt: datetime, end_dt: datetime) -> int:
    """Calculates deterministic crowd score for the traveler's preferred window."""
    base_crowd = calculate_crowd_score(destination_id)
    score = base_crowd.crowd_score

    # If falling on peak holiday dates, increase score
    if is_peak_holiday_window(start_dt) or is_peak_holiday_window(end_dt):
        if destination_id.lower() == "darjeeling":
            score = max(score, 92)
        else:
            score = min(85, score + 15)
    # If weekend heavy (Friday to Sunday)
    has_weekend = any((start_dt + timedelta(days=i)).weekday() in [5, 6] for i in range((end_dt - start_dt).days + 1))
    if has_weekend:
        score = min(98, score + 4)

    return min(100, max(10, score))

def get_date_alternatives(
    destination_id: str,
    preferred_start_date: str,
    preferred_end_date: str
) -> DateAlternativesResponse:
    """
    Generates 3 non-overlapping calm date windows for the selected destination.
    Calculates crowd score, classification, crowd reduction %, cost change, and structured explanations.
    """
    norm_id = destination_id.lower().strip()
    dest_map = {d["id"]: d for d in DESTINATIONS_DATA}
    if norm_id not in dest_map:
        raise KeyError(f"Destination '{destination_id}' not found")

    dest = dest_map[norm_id]
    start_dt = parse_date(preferred_start_date)
    end_dt = parse_date(preferred_end_date)

    if end_dt <= start_dt:
        raise ValueError("preferred_end_date must be strictly after preferred_start_date")

    duration = (end_dt - start_dt).days

    # Calculate baseline crowd for preferred dates
    pref_score = calculate_preferred_date_crowd(norm_id, start_dt, end_dt)
    pref_level, _ = classify_crowd_level(pref_score)

    # Deterministic alternative windows generation
    # Window 1: Shift to mid-week post-weekend or +11 days
    # Window 2: Shift +18 days
    # Window 3: Shift +25 days
    day_offsets = [11, 18, 25]

    # If preferred date is in late December (e.g. Dec 25), explicitly target early/mid January calm slots
    if start_dt.month == 12 and start_dt.day >= 20:
        year = start_dt.year + 1 if start_dt.month == 12 else start_dt.year
        target_windows = [
            (datetime(year, 1, 5), datetime(year, 1, 5) + timedelta(days=duration)),
            (datetime(year, 1, 8), datetime(year, 1, 8) + timedelta(days=duration)),
            (datetime(year, 1, 15), datetime(year, 1, 15) + timedelta(days=duration))
        ]
    else:
        target_windows = [
            (start_dt + timedelta(days=off), start_dt + timedelta(days=off + duration))
            for off in day_offsets
        ]

    # Baseline calm scores based on destination type
    if norm_id == "darjeeling":
        calm_scores = [36, 32, 28] # MEDIUM to LOW
        cost_deltas = ["-35%", "-40%", "-42%"]
        availabilities = [88, 92, 95]
        reasons = [
            "Post-holiday valley window with crystal clear Kanchenjunga visibility and 60% lower Mall Road pedestrian traffic.",
            "Mid-week tranquility with toy train tickets readily available and uncongested Hill Cart Road.",
            "Calmest seasonal window: hotel tariffs drop by over 40% with serene morning tea garden walks."
        ]
    elif norm_id == "kalimpong":
        calm_scores = [24, 20, 18]
        cost_deltas = ["-25%", "-30%", "-35%"]
        availabilities = [94, 96, 98]
        reasons = [
            "Optimal orchid blooming period with peaceful monastery prayer sessions and open Deolo viewpoints.",
            "Uncrowded ridge weather with pleasant temperate temperatures and ample homestay availability.",
            "Deep rural calm with zero vehicular delays along Teesta valley scenic routes."
        ]
    else:
        calm_scores = [18, 15, 14]
        cost_deltas = ["-20%", "-25%", "-30%"]
        availabilities = [95, 98, 99]
        reasons = [
            "Pristine forest canopy tranquility with minimum footprint on local eco-trails.",
            "Quiet alpine weather ideal for unobstructed mountain photography and dark sky stargazing.",
            "Homestays offer personalized hosting and organic fireside dinners with zero noise pollution."
        ]

    recommendations: List[DateAlternativeRecommendation] = []

    for i, (w_start, w_end) in enumerate(target_windows):
        w_score = calm_scores[i]
        w_level, _ = classify_crowd_level(w_score)
        
        reduction = max(0, int(round(((pref_score - w_score) / pref_score) * 100)))

        recommendations.append(
            DateAlternativeRecommendation(
                start_date=w_start.strftime("%Y-%m-%d"),
                end_date=w_end.strftime("%Y-%m-%d"),
                window_label=format_window_label(w_start, w_end),
                crowd_score=w_score,
                crowd_classification=w_level,
                crowd_reduction_percent=reduction,
                estimated_cost_change=cost_deltas[i],
                availability_score=availabilities[i],
                reason=reasons[i]
            )
        )

    return DateAlternativesResponse(
        destination_id=norm_id,
        destination_name=dest["name"],
        preferred_start_date=start_dt.strftime("%Y-%m-%d"),
        preferred_end_date=end_dt.strftime("%Y-%m-%d"),
        preferred_crowd_score=pref_score,
        preferred_crowd_classification=pref_level,
        date_alternatives=recommendations
    )
