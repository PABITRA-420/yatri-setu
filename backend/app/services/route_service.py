"""
Route Service for Yatri Setu (Smart India Hackathon 2026)
Provides regional transit estimates, road condition alerts, and eco-transit calculation.
Supports Mock provider for zero-dependency local execution, extensible to OpenRouteService/Google Maps.
"""

from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field

class RouteSegment(BaseModel):
    origin: str
    destination: str
    distance_km: float
    duration_minutes: int
    transit_mode: str = "Shared Himalayan Jeep"
    road_condition: str = "Paved mountain road with winding hairpin bends"
    elevation_gain_m: int = 0
    carbon_emissions_kg: float = 1.2
    shared_transit_available: bool = True
    is_demo_route: bool = True

class RouteSummary(BaseModel):
    total_distance_km: float
    total_duration_minutes: int
    segments: List[RouteSegment]
    recommended_mode: str
    eco_transit_note: str

# Curated regional inter-town distances & road profiles in the Darjeeling/Kalimpong circuit
INTER_TOWN_ROUTES: Dict[Tuple[str, str], Dict[str, Any]] = {
    ("darjeeling", "kalimpong"): {
        "distance_km": 50.0,
        "duration_minutes": 110,
        "road_condition": "Scenic descent via Peshok Tea Estate down to Teesta Bridge, followed by steady climb",
        "elevation_gain_m": 850,
        "shared_mode": "Shared Himalayan Jeep (Peshok Route)"
    },
    ("kalimpong", "darjeeling"): {
        "distance_km": 50.0,
        "duration_minutes": 110,
        "road_condition": "Descend to Teesta Bazaar and ascend through Peshok tea slopes",
        "elevation_gain_m": 850,
        "shared_mode": "Shared Himalayan Jeep (Peshok Route)"
    },
    ("kalimpong", "lava"): {
        "distance_km": 32.0,
        "duration_minutes": 75,
        "road_condition": "Smooth ridge road passing through pine plantations with occasional mist patches",
        "elevation_gain_m": 1100,
        "shared_mode": "Shared Local Jeep / Mini Bus"
    },
    ("lava", "kalimpong"): {
        "distance_km": 32.0,
        "duration_minutes": 75,
        "road_condition": "Descend from Neora pine belt into Kalimpong ridge",
        "elevation_gain_m": 400,
        "shared_mode": "Shared Local Jeep / Mini Bus"
    },
    ("lava", "lolegaon"): {
        "distance_km": 24.0,
        "duration_minutes": 65,
        "road_condition": "Forest road bordered by virgin oak and cypress canopies; slower scenic transit",
        "elevation_gain_m": 350,
        "shared_mode": "Eco Shared Shuttle or Local Gypsy"
    },
    ("lolegaon", "lava"): {
        "distance_km": 24.0,
        "duration_minutes": 65,
        "road_condition": "Oak forest stretch connecting Lolegaon heritage canopy to Lava",
        "elevation_gain_m": 350,
        "shared_mode": "Eco Shared Shuttle or Local Gypsy"
    },
    ("lava", "rishop"): {
        "distance_km": 4.5,
        "duration_minutes": 25,
        "road_condition": "Steep gravel mountain trail. Highly recommended 3.5 km walking trek through pine forest",
        "elevation_gain_m": 400,
        "shared_mode": "Forest Foot Trail or 4x4 Mountain Jeep"
    },
    ("rishop", "lava"): {
        "distance_km": 4.5,
        "duration_minutes": 25,
        "road_condition": "Steep descent via pine foot trail or 4x4 forest road",
        "elevation_gain_m": 100,
        "shared_mode": "Forest Foot Trail or 4x4 Mountain Jeep"
    },
    ("darjeeling", "mirik"): {
        "distance_km": 49.0,
        "duration_minutes": 105,
        "road_condition": "Picturesque hill road via Simana view point and Nepal border ridges",
        "elevation_gain_m": 600,
        "shared_mode": "Shared Hill Cart Jeep"
    },
    ("mirik", "darjeeling"): {
        "distance_km": 49.0,
        "duration_minutes": 105,
        "road_condition": "Ridge drive past orange orchards and Gopaldhara tea garden",
        "elevation_gain_m": 900,
        "shared_mode": "Shared Hill Cart Jeep"
    }
}

class BaseRouteProvider:
    def get_route(self, origin: str, destination: str, transit_mode: Optional[str] = None) -> RouteSegment:
        raise NotImplementedError

class MockRouteProvider(BaseRouteProvider):
    def get_route(self, origin: str, destination: str, transit_mode: Optional[str] = None) -> RouteSegment:
        norm_orig = origin.lower().strip()
        norm_dest = destination.lower().strip()

        # Check known inter-town route
        pair = (norm_orig, norm_dest)
        if pair in INTER_TOWN_ROUTES:
            info = INTER_TOWN_ROUTES[pair]
            mode = transit_mode or info["shared_mode"]
            # 80g CO2 per km for shared jeep vs 170g for private cab
            co2 = round(info["distance_km"] * (0.08 if "shared" in mode.lower() or "shuttle" in mode.lower() else 0.16), 2)
            return RouteSegment(
                origin=origin.title(),
                destination=destination.title(),
                distance_km=info["distance_km"],
                duration_minutes=info["duration_minutes"],
                transit_mode=mode,
                road_condition=info["road_condition"],
                elevation_gain_m=info["elevation_gain_m"],
                carbon_emissions_kg=co2,
                shared_transit_available=True,
                is_demo_route=True
            )

        # Intra-town attraction hopping default (within destination)
        if norm_orig == norm_dest:
            return RouteSegment(
                origin=origin.title(),
                destination=f"{origin.title()} Attractions",
                distance_km=6.5,
                duration_minutes=25,
                transit_mode=transit_mode or "Shared Electric Local Cab / Village Walk",
                road_condition="Local paved village lane with gentle gradients",
                elevation_gain_m=120,
                carbon_emissions_kg=0.3,
                shared_transit_available=True,
                is_demo_route=True
            )

        # Fallback for arbitrary points
        return RouteSegment(
            origin=origin.title(),
            destination=destination.title(),
            distance_km=28.0,
            duration_minutes=60,
            transit_mode=transit_mode or "Shared Himalayan Mountain Jeep",
            road_condition="Paved hill highway with seasonal mountain drainage channels",
            elevation_gain_m=450,
            carbon_emissions_kg=2.2,
            shared_transit_available=True,
            is_demo_route=True
        )

# Singleton provider instance
route_provider: BaseRouteProvider = MockRouteProvider()

def get_route_estimate(origin: str, destination: str, transit_mode: Optional[str] = None) -> RouteSegment:
    return route_provider.get_route(origin, destination, transit_mode)
