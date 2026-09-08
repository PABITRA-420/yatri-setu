from datetime import datetime
from typing import Dict, Any, List, Tuple
from app.models.crowd import CrowdLevel, CrowdResponse, CrowdFactorItem

WEIGHTS = {
    "historical_footfall": 0.35,
    "booking_density": 0.25,
    "seasonality": 0.15,
    "holiday_factor": 0.10,
    "weather_event_factor": 0.10,
    "traffic_factor": 0.05
}

# Detailed base raw indicators (0-100) for our curated destinations
DESTINATION_FACTOR_PROFILES: Dict[str, Dict[str, float]] = {
    "darjeeling": {
        "historical_footfall": 92.0,
        "booking_density": 90.0,
        "seasonality": 85.0,
        "holiday_factor": 80.0,
        "weather_event_factor": 80.0,
        "traffic_factor": 95.0
    },
    "kalimpong": {
        "historical_footfall": 45.0,
        "booking_density": 40.0,
        "seasonality": 48.0,
        "holiday_factor": 35.0,
        "weather_event_factor": 38.0,
        "traffic_factor": 25.0
    },
    "lava": {
        "historical_footfall": 25.0,
        "booking_density": 22.0,
        "seasonality": 28.0,
        "holiday_factor": 20.0,
        "weather_event_factor": 24.0,
        "traffic_factor": 15.0
    },
    "lolegaon": {
        "historical_footfall": 18.0,
        "booking_density": 16.0,
        "seasonality": 22.0,
        "holiday_factor": 15.0,
        "weather_event_factor": 20.0,
        "traffic_factor": 10.0
    },
    "rishop": {
        "historical_footfall": 15.0,
        "booking_density": 14.0,
        "seasonality": 18.0,
        "holiday_factor": 12.0,
        "weather_event_factor": 15.0,
        "traffic_factor": 5.0
    },
    "mirik": {
        "historical_footfall": 40.0,
        "booking_density": 36.0,
        "seasonality": 42.0,
        "holiday_factor": 35.0,
        "weather_event_factor": 32.0,
        "traffic_factor": 30.0
    }
}

FACTOR_METADATA = {
    "historical_footfall": {
        "name": "Historical Tourist Footfall",
        "weight": 35,
        "desc": "Aggregated seasonal tourist arrival patterns over recent seasons"
    },
    "booking_density": {
        "name": "Hotel & Homestay Booking Density",
        "weight": 25,
        "desc": "Current room reservations and peak accommodation occupancy rates"
    },
    "seasonality": {
        "name": "Seasonal Tourism Index",
        "weight": 15,
        "desc": "Optimal blooming and mountain visibility calendar window"
    },
    "holiday_factor": {
        "name": "Weekend & Holiday Multiplier",
        "weight": 10,
        "desc": "Long weekend travel influx from major urban hubs (Kolkata, Siliguri)"
    },
    "weather_event_factor": {
        "name": "Clear Sky & Weather Index",
        "weight": 10,
        "desc": "Favorable mountain visibility triggering spontaneous tourist surges"
    },
    "traffic_factor": {
        "name": "Transit Route & Bottleneck Density",
        "weight": 5,
        "desc": "Narrow mountain highway flow, parking saturation, and transit choke points"
    }
}

def classify_crowd_level(score: int) -> Tuple[CrowdLevel, str]:
    """
    Classify score:
    0-25: LOW (Emerald / Green)
    26-50: MEDIUM (Amber / Yellow)
    51-75: HIGH (Orange)
    76-100: VERY HIGH (Rose / Red)
    """
    if score <= 25:
        return CrowdLevel.LOW, "#10B981"
    elif score <= 50:
        return CrowdLevel.MEDIUM, "#F59E0B"
    elif score <= 75:
        return CrowdLevel.HIGH, "#F97316"
    else:
        return CrowdLevel.VERY_HIGH, "#E11D48"

def calculate_crowd_score(destination_id: str, custom_factors: Dict[str, float] = None) -> CrowdResponse:
    """
    Deterministic crowd score computation.
    crowd_score =
      35% historical_footfall +
      25% booking_density +
      15% seasonality +
      10% holiday_factor +
      10% weather_event_factor +
      5% traffic_factor
    """
    norm_id = destination_id.lower().strip()
    raw_factors = custom_factors or DESTINATION_FACTOR_PROFILES.get(norm_id, {
        "historical_footfall": 50.0,
        "booking_density": 50.0,
        "seasonality": 50.0,
        "holiday_factor": 50.0,
        "weather_event_factor": 50.0,
        "traffic_factor": 50.0
    })

    weighted_total = 0.0
    factor_items: List[CrowdFactorItem] = []

    for key, weight in WEIGHTS.items():
        raw_val = float(raw_factors.get(key, 50.0))
        weighted_val = raw_val * weight
        weighted_total += weighted_val

        meta = FACTOR_METADATA.get(key, {"name": key, "weight": int(weight * 100), "desc": ""})
        factor_items.append(
            CrowdFactorItem(
                name=meta["name"],
                key=key,
                raw_value=round(raw_val, 1),
                weight_percentage=meta["weight"],
                weighted_contribution=round(weighted_val, 1),
                description=meta["desc"]
            )
        )

    score = int(round(weighted_total))
    score = max(0, min(100, score))
    level, color = classify_crowd_level(score)

    dest_name = norm_id.capitalize()

    # Dynamic explanation generation
    why_crowded: List[str] = []
    bottlenecks: List[str] = []
    
    if norm_id == "darjeeling":
        why_crowded = [
            "Peak holiday season coinciding with clear sunrise views at Tiger Hill (95% observation deck saturation).",
            "Hill Cart Road and Mall Road experiencing severe vehicular queueing up to Ghoom railway crossing.",
            "Hotel & resort occupancy across Central Darjeeling is currently exceeding 91% capacity.",
            "Spillover day-trippers from Siliguri leading to prolonged pedestrian congestion at Chowrasta."
        ]
        bottlenecks = [
            "NH-110 Hill Cart Road (Ghoom to Station segment)",
            "Chowrasta Mall pedestrian zone between 4:00 PM and 7:30 PM",
            "Tiger Hill sunrise access gate between 3:45 AM and 5:30 AM"
        ]
        summary = "Darjeeling is currently experiencing extreme congestion across major landmarks, tea estates, and roads. Yatri Setu strongly advises diverting to calmer neighboring ridge towns like Kalimpong or Lava."
        peak_hours = "04:00 AM - 07:00 AM (Sunrise) & 04:30 PM - 08:00 PM (Mall Promenade)"
        best_time_today = "Early morning walks along secluded Tenzing Norgay Road (07:00 AM - 08:30 AM)"
        traffic_status = "Heavy Delays (+45 min transit time)"
        occupancy = "91% (Critical)"

    elif norm_id == "kalimpong":
        why_crowded = [
            "Balanced visitor movement with steady interest in local orchid nurseries and heritage schools.",
            "Uncongested arterial roads with comfortable parking availability at Deolo Hill.",
            "Homestays are operating at sustainable 45% capacity, ensuring personalized host hospitality."
        ]
        bottlenecks = ["Motor Stand junction during morning school hours (08:15 AM - 09:00 AM)"]
        summary = "Kalimpong has moderate, peaceful footfall with ample breathing space, serene monasteries, and active orchid nurseries."
        peak_hours = "11:00 AM - 01:30 PM (Deolo Park summit)"
        best_time_today = "Anytime; Deolo Hill is best enjoyed between 09:00 AM - 11:30 AM"
        traffic_status = "Smooth / Normal Flow"
        occupancy = "44% (Healthy & Readily Available)"

    elif norm_id in ["lava", "lolegaon", "rishop"]:
        why_crowded = [
            "Low ecological footprint with wide open pine woodlands and tranquil rural trails.",
            "Zero traffic lights or congestion; foot travel and small village jeep tracks only.",
            "Homestays provide authentic home hospitality with quiet, starlit night skies."
        ]
        bottlenecks = ["Narrow single-lane mountain forest turns; drive at moderate speeds"]
        summary = f"{dest_name} enjoys serene low-crowd tranquility. Ideal for eco-conscious travelers seeking pristine nature and zero urban noise."
        peak_hours = "None; calm throughout the day"
        best_time_today = "Whole day; early morning canopy trails recommended"
        traffic_status = "Uncongested / Pristine Mountain Roads"
        occupancy = "22% - 30% (Abundant Openings)"

    else:
        why_crowded = [
            "Moderate visitor influx concentrated around the primary lake promenade and market.",
            "Steady local tourist movement without prolonged transit bottlenecks."
        ]
        bottlenecks = ["Lakeside entry parking zone"]
        summary = f"{dest_name} has moderate crowd levels with relaxed scenic avenues."
        peak_hours = "01:00 PM - 04:00 PM"
        best_time_today = "Morning lakeside strolls (07:30 AM - 10:00 AM)"
        traffic_status = "Normal Mountain Flow"
        occupancy = "42% (Normal)"

    return CrowdResponse(
        destination_id=norm_id,
        destination_name=dest_name,
        crowd_score=score,
        crowd_level=level,
        color_code=color,
        summary=summary,
        why_crowded=why_crowded,
        bottlenecks=bottlenecks,
        peak_visiting_hours=peak_hours,
        best_time_to_visit_today=best_time_today,
        factors=factor_items,
        live_traffic_status=traffic_status,
        hotel_occupancy_rate=occupancy,
        last_updated=datetime.now().strftime("%I:%M %p, Today")
    )
