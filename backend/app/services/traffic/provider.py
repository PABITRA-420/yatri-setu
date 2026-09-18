"""
Traffic Providers Implementation for Yatri Setu (Milestone 7C).
Simulates multi-route mountain arterial corridors and supports external provider integrations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from app.core.config import settings
from app.services.traffic.base import BaseTrafficProvider
from app.services.traffic.schemas import RouteTrafficObservation, DestinationTrafficSummary

logger = logging.getLogger(__name__)

# Multi-corridor mountain road network models
DEMO_CORRIDOR_DATA: Dict[str, Dict[str, Any]] = {
    "darjeeling": {
        "name": "Darjeeling",
        "routes": [
            {
                "route_id": "rt-darj-nh55",
                "route_name": "Hill Cart Road (NH 55) & Ghoom Intersection",
                "origin": "Siliguri / Sukna",
                "current_min": 145,
                "hist_min": 90,
                "road_status": "RESTRICTED",
                "incidents": 1,
                "incident_desc": "Ghoom toy train level-crossing delay & single-lane urban bottlenecks"
            },
            {
                "route_id": "rt-darj-rohini",
                "route_name": "Rohini Mountain Toll Bypass",
                "origin": "Kurseong Ridge",
                "current_min": 95,
                "hist_min": 75,
                "road_status": "SLOW",
                "incidents": 0,
                "incident_desc": None
            },
            {
                "route_id": "rt-darj-pankhabari",
                "route_name": "Pankhabari Heritage Route",
                "origin": "Matigara",
                "current_min": 85,
                "hist_min": 80,
                "road_status": "CLEAR",
                "incidents": 0,
                "incident_desc": None
            }
        ]
    },
    "kalimpong": {
        "name": "Kalimpong",
        "routes": [
            {
                "route_id": "rt-kalim-nh10",
                "route_name": "NH 10 Teesta Corridor & Teesta Bridge",
                "origin": "Siliguri / Coronation Bridge",
                "current_min": 92,
                "hist_min": 70,
                "road_status": "SLOW",
                "incidents": 0,
                "incident_desc": "Teesta police one-way traffic regulation active"
            },
            {
                "route_id": "rt-kalim-rishi",
                "route_name": "Rishi Road Mountain Artery",
                "origin": "Pedong / Algarah",
                "current_min": 38,
                "hist_min": 35,
                "road_status": "CLEAR",
                "incidents": 0,
                "incident_desc": None
            }
        ]
    },
    "lava": {
        "name": "Lava",
        "routes": [
            {
                "route_id": "rt-lava-algarah",
                "route_name": "Algarah-Lava Pine Forest Road",
                "origin": "Kalimpong / Algarah",
                "current_min": 48,
                "hist_min": 45,
                "road_status": "CLEAR",
                "incidents": 0,
                "incident_desc": None
            },
            {
                "route_id": "rt-lava-gorubathan",
                "route_name": "Gorubathan-Lava Forest Highway",
                "origin": "Damdim / Dooars",
                "current_min": 62,
                "hist_min": 60,
                "road_status": "CLEAR",
                "incidents": 0,
                "incident_desc": None
            }
        ]
    },
    "lolegaon": {
        "name": "Lolegaon",
        "routes": [
            {
                "route_id": "rt-lole-lava",
                "route_name": "Lava-Lolegaon Heritage Stretch",
                "origin": "Lava",
                "current_min": 32,
                "hist_min": 30,
                "road_status": "CLEAR",
                "incidents": 0,
                "incident_desc": None
            }
        ]
    },
    "rishop": {
        "name": "Rishop",
        "routes": [
            {
                "route_id": "rt-rishop-trail",
                "route_name": "Upper Rishop Eco-Jeep Trail",
                "origin": "Lava Crossing",
                "current_min": 25,
                "hist_min": 25,
                "road_status": "CLEAR",
                "incidents": 0,
                "incident_desc": None
            }
        ]
    },
    "mirik": {
        "name": "Mirik",
        "routes": [
            {
                "route_id": "rt-mirik-kurseong",
                "route_name": "Mirik-Kurseong Ridge Highway",
                "origin": "Siliguri / Dudhia",
                "current_min": 72,
                "hist_min": 60,
                "road_status": "SLOW",
                "incidents": 0,
                "incident_desc": "Minor slowdown near lake entrance"
            },
            {
                "route_id": "rt-mirik-soureni",
                "route_name": "Soureni Tea Estate Link",
                "origin": "Pashupati Phatak",
                "current_min": 42,
                "hist_min": 40,
                "road_status": "CLEAR",
                "incidents": 0,
                "incident_desc": None
            }
        ]
    }
}


def classify_route_congestion(ratio: float) -> str:
    """Classifies travel-time ratio into standardized congestion level."""
    if ratio >= 1.8:
        return "CRITICAL"
    elif ratio >= 1.4:
        return "HIGH"
    elif ratio >= 1.15:
        return "ELEVATED"
    return "NORMAL"


class DemoTrafficProvider(BaseTrafficProvider):
    """
    High-fidelity deterministic simulator for mountain corridor traffic.
    Tracks multiple routes per destination and determines arterial chokepoints.
    """

    def is_available(self) -> bool:
        return True

    def get_provider_mode(self) -> str:
        return "DEMO"

    def fetch_traffic(self, destination_id: str) -> DestinationTrafficSummary:
        dest_clean = destination_id.lower().strip()
        data = DEMO_CORRIDOR_DATA.get(dest_clean, DEMO_CORRIDOR_DATA["kalimpong"])
        now = datetime.utcnow()

        routes_obs: List[RouteTrafficObservation] = []
        total_ratio = 0.0
        total_incidents = 0
        has_closed = False
        has_restricted = False
        primary_bottleneck = None
        max_ratio = 0.0

        for r in data["routes"]:
            cur = r["current_min"]
            hist = r["hist_min"]
            ratio = round(cur / hist, 2)
            anomaly_pct = round(((cur - hist) / hist) * 100, 1)
            level = classify_route_congestion(ratio)

            obs = RouteTrafficObservation(
                route_id=r["route_id"],
                route_name=r["route_name"],
                origin=r["origin"],
                destination_id=dest_clean,
                current_travel_time_min=cur,
                historical_travel_time_min=hist,
                travel_time_ratio=ratio,
                travel_time_anomaly_percent=anomaly_pct,
                congestion_level=level,
                road_status=r["road_status"],
                incident_count=r["incidents"],
                incident_description=r["incident_desc"]
            )
            routes_obs.append(obs)

            total_ratio += ratio
            total_incidents += r["incidents"]
            if r["road_status"] == "CLOSED":
                has_closed = True
            elif r["road_status"] == "RESTRICTED":
                has_restricted = True

            if ratio > max_ratio and ratio > 1.15:
                max_ratio = ratio
                primary_bottleneck = r["route_name"]

        route_count = max(1, len(routes_obs))
        avg_ratio = round(total_ratio / route_count, 2)
        avg_anomaly = round(((avg_ratio - 1.0) * 100), 1)

        # Congestion score 0-100: ratio 1.0 -> 20, 1.3 -> 50, 1.6 -> 80, 2.0 -> 100
        congestion_score = round(max(0.0, min(100.0, (avg_ratio - 0.8) * 80.0)), 1)

        # Access Status separation
        if has_closed:
            access = "DISRUPTED"
        elif has_restricted or avg_ratio >= 1.4 or total_incidents > 0:
            access = "CAUTION"
        else:
            access = "OPEN"

        return DestinationTrafficSummary(
            destination_id=dest_clean,
            destination_name=data["name"],
            overall_congestion_score=congestion_score,
            average_travel_time_ratio=avg_ratio,
            travel_time_anomaly_percent=avg_anomaly,
            incident_count=total_incidents,
            access_status=access,
            primary_bottleneck_route=primary_bottleneck,
            critical_routes=routes_obs,
            observed_at=now,
            source="DEMO_HIMALAYAN_CORRIDOR_TELEMETRY",
            provider_mode="DEMO",
            provenance_label="DEMO MODE — SYNTHETIC DATA",
            confidence=0.90,
            data_quality="HIGH",
            fetched_at=now,
            cache_status="LIVE"
        )


# Canonical GPS coordinates for TomTom corridor queries:
# (origin_lat, origin_lon, dest_lat, dest_lon)
TOMTOM_CORRIDOR_WAYPOINTS: Dict[str, List[Dict[str, Any]]] = {
    "darjeeling": [
        {
            "route_id": "rt-darj-nh55",
            "route_name": "Hill Cart Road (NH 55) & Ghoom Intersection",
            "origin": "Siliguri / Sukna",
            "origin_coords": (26.7900, 88.3600),
            "dest_coords": (27.0410, 88.2663),
            "historical_min": 90,
        },
        {
            "route_id": "rt-darj-rohini",
            "route_name": "Rohini Mountain Toll Bypass",
            "origin": "Kurseong Ridge",
            "origin_coords": (26.8800, 88.2800),
            "dest_coords": (27.0410, 88.2663),
            "historical_min": 75,
        },
        {
            "route_id": "rt-darj-pankhabari",
            "route_name": "Pankhabari Heritage Route",
            "origin": "Matigara",
            "origin_coords": (26.7200, 88.3700),
            "dest_coords": (27.0410, 88.2663),
            "historical_min": 80,
        }
    ],
    "kalimpong": [
        {
            "route_id": "rt-kalim-nh10",
            "route_name": "NH 10 Teesta Corridor & Teesta Bridge",
            "origin": "Siliguri / Coronation Bridge",
            "origin_coords": (26.8850, 88.4700),
            "dest_coords": (27.0594, 88.4695),
            "historical_min": 70,
        },
        {
            "route_id": "rt-kalim-rishi",
            "route_name": "Rishi Road Mountain Artery",
            "origin": "Pedong / Algarah",
            "origin_coords": (27.1100, 88.5800),
            "dest_coords": (27.0594, 88.4695),
            "historical_min": 35,
        }
    ],
    "lava": [
        {
            "route_id": "rt-lava-algarah",
            "route_name": "Algarah-Lava Pine Forest Road",
            "origin": "Kalimpong / Algarah",
            "origin_coords": (27.1100, 88.5800),
            "dest_coords": (27.0864, 88.6603),
            "historical_min": 45,
        },
        {
            "route_id": "rt-lava-gorubathan",
            "route_name": "Gorubathan-Lava Forest Highway",
            "origin": "Damdim / Dooars",
            "origin_coords": (26.8900, 88.7000),
            "dest_coords": (27.0864, 88.6603),
            "historical_min": 60,
        }
    ],
    "lolegaon": [
        {
            "route_id": "rt-lole-canopy",
            "route_name": "Lava-Lolegaon Ridge Trail",
            "origin": "Lava Junction",
            "origin_coords": (27.0864, 88.6603),
            "dest_coords": (27.0142, 88.5583),
            "historical_min": 40,
        }
    ],
    "rishop": [
        {
            "route_id": "rt-rishop-ridge",
            "route_name": "Lava-Rishop Mountain Track",
            "origin": "Lava Monastery",
            "origin_coords": (27.0864, 88.6603),
            "dest_coords": (27.1065, 88.6496),
            "historical_min": 25,
        }
    ],
    "mirik": [
        {
            "route_id": "rt-mirik-kurseong",
            "route_name": "Mirik-Kurseong Ridge Road",
            "origin": "Kurseong / Pankhabari",
            "origin_coords": (26.8800, 88.2800),
            "dest_coords": (26.9011, 88.1755),
            "historical_min": 50,
        },
        {
            "route_id": "rt-mirik-simana",
            "route_name": "Simana Viewpoint & Indo-Nepal Border Highway",
            "origin": "Pashupati Border",
            "origin_coords": (26.9200, 88.1400),
            "dest_coords": (26.9011, 88.1755),
            "historical_min": 30,
        }
    ]
}


_UNSET = object()


class TomTomTrafficProvider(BaseTrafficProvider):
    """
    Genuine TomTom Traffic & Routing API adapter.
    Queries TomTom calculateRoute endpoint with traffic=true to compute
    exact travel time with live delays versus historical free-flow conditions.
    """

    def __init__(self, api_key: Any = _UNSET, timeout: float = 6.0):
        if api_key is not _UNSET:
            raw_key = api_key
        else:
            raw_key = getattr(settings, "TOMTOM_API_KEY", None) or settings.TRAFFIC_API_KEY
        
        if raw_key:
            cleaned = str(raw_key).strip().strip('"').strip("'")
            if len(cleaned) == 38 and cleaned.endswith("tomtom"):
                cleaned = cleaned[:-6]
            self.api_key = cleaned if cleaned else None
        else:
            self.api_key = None

        self.timeout = timeout
        self._last_connectivity_check: Optional[tuple] = None

    def check_connectivity(self, force: bool = False) -> bool:
        """
        Tests actual provider connectivity and authentication against TomTom API.
        Caches result for 60 seconds to avoid API quota drain and health check latency.
        """
        if not self.api_key or not self.api_key.strip():
            return False

        now = datetime.utcnow()
        if not force and self._last_connectivity_check is not None:
            last_time, status = self._last_connectivity_check
            if (now - last_time).total_seconds() < 60:
                return status

        # Fast minimal probe on a known route (Siliguri region)
        test_url = (
            f"https://api.tomtom.com/routing/1/calculateRoute/"
            f"26.7200,88.4200:26.7250,88.4250/json?key={self.api_key}&traffic=false"
        )
        import httpx
        try:
            with httpx.Client(timeout=httpx.Timeout(3.0, connect=1.5)) as client:
                resp = client.get(test_url)
                is_connected = (resp.status_code == 200)
                self._last_connectivity_check = (now, is_connected)
                return is_connected
        except Exception as e:
            logger.debug(f"TomTom connectivity check failed: {e}")
            self._last_connectivity_check = (now, False)
            return False

    def is_available(self) -> bool:
        return self.check_connectivity()

    def get_provider_mode(self) -> str:
        return "REAL"

    def fetch_traffic(self, destination_id: str) -> DestinationTrafficSummary:
        dest_clean = destination_id.lower().strip()
        if not self.api_key or not self.api_key.strip():
            raise RuntimeError("TomTom traffic provider API key is not configured")

        corridors = TOMTOM_CORRIDOR_WAYPOINTS.get(dest_clean)
        if not corridors:
            raise ValueError(f"Unknown destination '{destination_id}' for traffic telemetry")

        now = datetime.utcnow()
        routes_obs: List[RouteTrafficObservation] = []
        total_ratio = 0.0
        total_incidents = 0
        max_ratio = 1.0
        primary_bottleneck = None
        has_closed = False
        has_restricted = False

        import httpx

        # Query live traffic for each corridor with persistent client session
        with httpx.Client(timeout=httpx.Timeout(self.timeout, connect=2.0)) as client:
            for corridor in corridors:
                orig_lat, orig_lon = corridor["origin_coords"]
                dest_lat, dest_lon = corridor["dest_coords"]
                fallback_hist_min = corridor["historical_min"]

                url = (
                    f"https://api.tomtom.com/routing/1/calculateRoute/"
                    f"{orig_lat:.4f},{orig_lon:.4f}:{dest_lat:.4f},{dest_lon:.4f}/json"
                    f"?key={self.api_key}&traffic=true&travelMode=car&computeTravelTimeFor=all"
                )

                try:
                    resp = client.get(url)
                    if resp.status_code != 200:
                        logger.warning(
                            f"TomTom API returned status {resp.status_code} for {corridor['route_id']}: {resp.text[:100]}"
                        )
                        self._last_connectivity_check = (now, False)
                        raise RuntimeError(f"TomTom API error HTTP {resp.status_code}")

                    data = resp.json()
                    routes_data = data.get("routes", [])
                    if not routes_data or not isinstance(routes_data, list):
                        raise ValueError(f"Malformed TomTom response: missing routes for {corridor['route_id']}")

                    summary = routes_data[0].get("summary", {})
                    if not summary or not isinstance(summary, dict):
                        raise ValueError(f"Malformed TomTom response: missing summary for {corridor['route_id']}")

                    travel_time_sec = summary.get("travelTimeInSeconds")
                    if travel_time_sec is None:
                        raise ValueError(f"Malformed TomTom response: missing travelTimeInSeconds for {corridor['route_id']}")

                    no_traffic_sec = summary.get("noTrafficTravelTimeInSeconds") or summary.get("historicTrafficTravelTimeInSeconds")
                    delay_sec = summary.get("trafficDelayInSeconds", 0)

                    cur_min = max(1, int(round(travel_time_sec / 60.0)))
                    if no_traffic_sec and no_traffic_sec > 0:
                        hist_min = max(1, int(round(no_traffic_sec / 60.0)))
                    else:
                        hist_min = fallback_hist_min

                except Exception as e:
                    logger.warning(f"TomTom corridor query failed for {corridor['route_id']}: {e}")
                    raise

                ratio = round(cur_min / max(1, hist_min), 2)
                anomaly_pct = round(((cur_min - hist_min) / max(1, hist_min)) * 100.0, 1)

                incident_desc = None
                if delay_sec >= 900 or ratio >= 1.6:
                    road_status = "RESTRICTED"
                    has_restricted = True
                    total_incidents += 1
                    incident_desc = f"TomTom Traffic Alert: {delay_sec // 60}m congestion delay along corridor"
                elif delay_sec >= 300 or ratio >= 1.25:
                    road_status = "SLOW"
                    total_incidents += 1
                    incident_desc = f"TomTom Delay: {delay_sec // 60}m transit slowdown"
                elif delay_sec > 60:
                    road_status = "SLOW"
                    incident_desc = f"TomTom Delay: {delay_sec // 60}m minor delay"
                else:
                    road_status = "CLEAR"

                level = classify_route_congestion(ratio)

                obs = RouteTrafficObservation(
                    route_id=corridor["route_id"],
                    route_name=corridor["route_name"],
                    origin=corridor["origin"],
                    destination_id=dest_clean,
                    current_travel_time_min=cur_min,
                    historical_travel_time_min=hist_min,
                    travel_time_ratio=ratio,
                    travel_time_anomaly_percent=anomaly_pct,
                    congestion_level=level,
                    road_status=road_status,
                    incident_count=1 if incident_desc else 0,
                    incident_description=incident_desc
                )
                routes_obs.append(obs)

                total_ratio += ratio
                if ratio > max_ratio and ratio > 1.15:
                    max_ratio = ratio
                    primary_bottleneck = corridor["route_name"]

        route_count = max(1, len(routes_obs))
        avg_ratio = round(total_ratio / route_count, 2)
        avg_anomaly = round(((avg_ratio - 1.0) * 100.0), 1)

        congestion_score = round(max(0.0, min(100.0, (avg_ratio - 0.8) * 80.0)), 1)

        if has_closed:
            access = "DISRUPTED"
        elif has_restricted or avg_ratio >= 1.4 or total_incidents > 0:
            access = "CAUTION"
        else:
            access = "OPEN"

        dest_name = dest_clean.capitalize()
        if dest_clean in DEMO_CORRIDOR_DATA:
            dest_name = DEMO_CORRIDOR_DATA[dest_clean]["name"]

        self._last_connectivity_check = (now, True)

        return DestinationTrafficSummary(
            destination_id=dest_clean,
            destination_name=dest_name,
            overall_congestion_score=congestion_score,
            average_travel_time_ratio=avg_ratio,
            travel_time_anomaly_percent=avg_anomaly,
            incident_count=total_incidents,
            access_status=access,
            primary_bottleneck_route=primary_bottleneck,
            critical_routes=routes_obs,
            observed_at=now,
            source="TOMTOM_LIVE_TRAFFIC",
            provider_mode="REAL",
            provenance_label="REAL — TOMTOM TRAFFIC",
            confidence=0.95,
            data_quality="HIGH",
            fetched_at=now,
            cache_status="LIVE"
        )


# Backward-compatible alias
RealTrafficProvider = TomTomTrafficProvider


class UnavailableTrafficProvider(BaseTrafficProvider):
    """Fallback provider when traffic feeds are offline."""

    def is_available(self) -> bool:
        return False

    def get_provider_mode(self) -> str:
        return "UNAVAILABLE"

    def fetch_traffic(self, destination_id: str) -> DestinationTrafficSummary:
        dest_clean = destination_id.lower().strip()
        now = datetime.utcnow()
        return DestinationTrafficSummary(
            destination_id=dest_clean,
            destination_name=dest_clean.title(),
            overall_congestion_score=30.0,
            average_travel_time_ratio=1.0,
            travel_time_anomaly_percent=0.0,
            incident_count=0,
            access_status="UNKNOWN",
            primary_bottleneck_route=None,
            critical_routes=[],
            observed_at=now,
            source="TRAFFIC_PROVIDER_UNAVAILABLE",
            provider_mode="UNAVAILABLE",
            provenance_label="UNAVAILABLE — SAFE FALLBACK",
            confidence=0.0,
            data_quality="UNKNOWN",
            fetched_at=now,
            cache_status="UNAVAILABLE"
        )
