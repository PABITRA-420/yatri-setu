"""
High-fidelity Demo Route Provider for Yatri Setu Eastern Himalayan Circuit.
Provides realistic mountain road corridors with actual arterial waypoints.
"""

from typing import Dict, Tuple, List, Optional, Any
from app.services.routing.base import BaseRoutingProvider
from app.services.routing.schemas import RouteCalculationResponse, RouteGeometry
from app.services.routing.coordinates import CIRCUIT_COORDINATES, CIRCUIT_NAMES

# Curated corridor geometry waypoints [lon, lat] tracking actual mountain highways
ROAD_WAYPOINTS: Dict[Tuple[str, str], List[List[float]]] = {
    ("darjeeling", "kalimpong"): [
        [88.2663, 27.0410],  # Darjeeling Mall / Chowrasta
        [88.2580, 27.0180],  # Ghoom Station
        [88.2720, 27.0100],  # Jorebungalow junction
        [88.3150, 27.0250],  # 3rd Mile / Senchal forest edge
        [88.3580, 27.0420],  # 6th Mile Takdah junction
        [88.3950, 27.0610],  # Peshok Tea Estate hairpin descent
        [88.4280, 27.0540],  # Teesta Bazaar Bridge (River crossing)
        [88.4480, 27.0490],  # 10th Mile climb
        [88.4695, 27.0594],  # Kalimpong Town Center
    ],
    ("kalimpong", "darjeeling"): [
        [88.4695, 27.0594],
        [88.4480, 27.0490],
        [88.4280, 27.0540],
        [88.3950, 27.0610],
        [88.3580, 27.0420],
        [88.3150, 27.0250],
        [88.2720, 27.0100],
        [88.2580, 27.0180],
        [88.2663, 27.0410],
    ],
    ("kalimpong", "lava"): [
        [88.4695, 27.0594],  # Kalimpong
        [88.5150, 27.0850],  # Dr. Graham's Homes ridge
        [88.5520, 27.1020],  # Pedong cutoff
        [88.5830, 27.1120],  # Algarah Bazaar
        [88.6250, 27.1010],  # Neora Valley pine canopy
        [88.6603, 27.0864],  # Lava Monastery hamlet
    ],
    ("lava", "kalimpong"): [
        [88.6603, 27.0864],
        [88.6250, 27.1010],
        [88.5830, 27.1120],
        [88.5520, 27.1020],
        [88.5150, 27.0850],
        [88.4695, 27.0594],
    ],
    ("lava", "lolegaon"): [
        [88.6603, 27.0864],  # Lava
        [88.6320, 27.0650],  # Upper Kafer virgin forest
        [88.5980, 27.0380],  # Oak canopy stretch
        [88.5720, 27.0220],  # Jhandi Dara approach
        [88.5583, 27.0142],  # Lolegaon
    ],
    ("lolegaon", "lava"): [
        [88.5583, 27.0142],
        [88.5720, 27.0220],
        [88.5980, 27.0380],
        [88.6320, 27.0650],
        [88.6603, 27.0864],
    ],
    ("lava", "rishop"): [
        [88.6603, 27.0864],  # Lava
        [88.6560, 27.0950],  # Neora ridge pine trail
        [88.6520, 27.1020],  # Tiffin Dara view ridge
        [88.6496, 27.1065],  # Rishop view settlement
    ],
    ("rishop", "lava"): [
        [88.6496, 27.1065],
        [88.6520, 27.1020],
        [88.6560, 27.0950],
        [88.6603, 27.0864],
    ],
    ("darjeeling", "mirik"): [
        [88.2663, 27.0410],  # Darjeeling
        [88.2560, 27.0150],  # Ghoom
        [88.2120, 26.9920],  # Sukhia Pokhari
        [88.1920, 26.9550],  # Lepchajagat pine forest
        [88.1820, 26.9280],  # Simana viewpoint
        [88.1755, 26.9011],  # Mirik Sumendu Lake
    ],
    ("mirik", "darjeeling"): [
        [88.1755, 26.9011],
        [88.1820, 26.9280],
        [88.1920, 26.9550],
        [88.2120, 26.9920],
        [88.2560, 27.0150],
        [88.2663, 27.0410],
    ],
    ("darjeeling", "lava"): [
        [88.2663, 27.0410],
        [88.2580, 27.0180],
        [88.3580, 27.0420],
        [88.4280, 27.0540],
        [88.4695, 27.0594],
        [88.5830, 27.1120],
        [88.6603, 27.0864],
    ],
    ("lava", "darjeeling"): [
        [88.6603, 27.0864],
        [88.5830, 27.1120],
        [88.4695, 27.0594],
        [88.4280, 27.0540],
        [88.3580, 27.0420],
        [88.2580, 27.0180],
        [88.2663, 27.0410],
    ],
}

# Road profile metrics
DEMO_CORRIDOR_PROFILES: Dict[Tuple[str, str], Dict[str, Any]] = {
    ("darjeeling", "kalimpong"): {
        "distance_km": 50.0,
        "duration_minutes": 110,
        "transit_mode": "Shared Himalayan Jeep (Peshok Route)",
        "road_condition": "Scenic descent via Peshok Tea Estate down to Teesta Bridge, followed by steady climb",
        "elevation_gain_m": 850,
        "carbon_emissions_kg": 4.0
    },
    ("kalimpong", "darjeeling"): {
        "distance_km": 50.0,
        "duration_minutes": 110,
        "transit_mode": "Shared Himalayan Jeep (Peshok Route)",
        "road_condition": "Descend to Teesta Bazaar and ascend through Peshok tea slopes",
        "elevation_gain_m": 850,
        "carbon_emissions_kg": 4.0
    },
    ("kalimpong", "lava"): {
        "distance_km": 32.0,
        "duration_minutes": 75,
        "transit_mode": "Shared Local Jeep / Mini Bus",
        "road_condition": "Smooth ridge road passing through pine plantations with occasional mist patches",
        "elevation_gain_m": 1100,
        "carbon_emissions_kg": 2.5
    },
    ("lava", "kalimpong"): {
        "distance_km": 32.0,
        "duration_minutes": 75,
        "transit_mode": "Shared Local Jeep / Mini Bus",
        "road_condition": "Descend from Neora pine belt into Kalimpong ridge",
        "elevation_gain_m": 400,
        "carbon_emissions_kg": 2.5
    },
    ("lava", "lolegaon"): {
        "distance_km": 24.0,
        "duration_minutes": 65,
        "transit_mode": "Eco Shared Shuttle or Local Gypsy",
        "road_condition": "Forest road bordered by virgin oak and cypress canopies; slower scenic transit",
        "elevation_gain_m": 350,
        "carbon_emissions_kg": 1.9
    },
    ("lolegaon", "lava"): {
        "distance_km": 24.0,
        "duration_minutes": 65,
        "transit_mode": "Eco Shared Shuttle or Local Gypsy",
        "road_condition": "Oak forest stretch connecting Lolegaon heritage canopy to Lava",
        "elevation_gain_m": 350,
        "carbon_emissions_kg": 1.9
    },
    ("lava", "rishop"): {
        "distance_km": 4.5,
        "duration_minutes": 25,
        "transit_mode": "Forest Foot Trail or 4x4 Mountain Jeep",
        "road_condition": "Steep gravel mountain trail. Highly recommended walking trek through pine forest",
        "elevation_gain_m": 400,
        "carbon_emissions_kg": 0.4
    },
    ("rishop", "lava"): {
        "distance_km": 4.5,
        "duration_minutes": 25,
        "transit_mode": "Forest Foot Trail or 4x4 Mountain Jeep",
        "road_condition": "Steep descent via pine foot trail or 4x4 forest road",
        "elevation_gain_m": 100,
        "carbon_emissions_kg": 0.4
    },
    ("darjeeling", "mirik"): {
        "distance_km": 49.0,
        "duration_minutes": 105,
        "transit_mode": "Shared Hill Cart Jeep",
        "road_condition": "Picturesque hill road via Simana view point and Nepal border ridges",
        "elevation_gain_m": 600,
        "carbon_emissions_kg": 3.9
    },
    ("mirik", "darjeeling"): {
        "distance_km": 49.0,
        "duration_minutes": 105,
        "transit_mode": "Shared Hill Cart Jeep",
        "road_condition": "Ridge drive past orange orchards and Gopaldhara tea garden",
        "elevation_gain_m": 900,
        "carbon_emissions_kg": 3.9
    },
    ("darjeeling", "lava"): {
        "distance_km": 78.0,
        "duration_minutes": 160,
        "transit_mode": "Arterial Hill Cab / Jeep",
        "road_condition": "Descent via Peshok, Teesta bridge, Kalimpong bypass to Lava pine forests",
        "elevation_gain_m": 1250,
        "carbon_emissions_kg": 6.2
    },
    ("lava", "darjeeling"): {
        "distance_km": 78.0,
        "duration_minutes": 160,
        "transit_mode": "Arterial Hill Cab / Jeep",
        "road_condition": "Scenic cross-corridor transit via Kalimpong and Teesta Valley",
        "elevation_gain_m": 1250,
        "carbon_emissions_kg": 6.2
    },
}


class DemoRouteProvider(BaseRoutingProvider):
    """
    Synthetic high-fidelity road routing provider using realistic mountain road corridors.
    """

    def is_available(self) -> bool:
        return True

    def get_provider_name(self) -> str:
        return "demo"

    def get_provenance_label(self) -> str:
        return "DEMO MODE — SYNTHETIC DATA"

    def calculate_route(
        self,
        origin_id: str,
        destination_id: str,
        transit_mode: Optional[str] = None
    ) -> RouteCalculationResponse:
        norm_orig = origin_id.lower().strip()
        norm_dest = destination_id.lower().strip()

        if norm_orig not in CIRCUIT_COORDINATES:
            raise ValueError(f"Unknown origin destination: '{origin_id}'")
        if norm_dest not in CIRCUIT_COORDINATES:
            raise ValueError(f"Unknown destination: '{destination_id}'")

        lat1, lon1 = CIRCUIT_COORDINATES[norm_orig]
        lat2, lon2 = CIRCUIT_COORDINATES[norm_dest]

        pair = (norm_orig, norm_dest)

        # Intra-town (same origin and destination)
        if norm_orig == norm_dest:
            return RouteCalculationResponse(
                origin_destination_id=norm_orig,
                origin_name=CIRCUIT_NAMES[norm_orig],
                destination_destination_id=norm_dest,
                destination_name=f"{CIRCUIT_NAMES[norm_dest]} Local Circuit",
                distance_km=6.5,
                duration_minutes=25,
                route_geometry=RouteGeometry(coordinates=[
                    [lon1, lat1],
                    [lon1 + 0.005, lat1 + 0.004],
                    [lon1 + 0.008, lat1 - 0.003],
                    [lon1, lat1]
                ]),
                provider="demo",
                provenance_label=self.get_provenance_label(),
                is_road_distance=True,
                transit_mode=transit_mode or "Shared Electric Local Cab / Village Walk",
                road_condition="Local paved village lane with gentle mountain gradients",
                elevation_gain_m=120,
                carbon_emissions_kg=0.3,
                notes="Curated intra-town sight corridor"
            )

        # Check known corridor
        if pair in ROAD_WAYPOINTS and pair in DEMO_CORRIDOR_PROFILES:
            waypoints = ROAD_WAYPOINTS[pair]
            profile = DEMO_CORRIDOR_PROFILES[pair]
            return RouteCalculationResponse(
                origin_destination_id=norm_orig,
                origin_name=CIRCUIT_NAMES[norm_orig],
                destination_destination_id=norm_dest,
                destination_name=CIRCUIT_NAMES[norm_dest],
                distance_km=profile["distance_km"],
                duration_minutes=profile["duration_minutes"],
                route_geometry=RouteGeometry(coordinates=waypoints),
                provider="demo",
                provenance_label=self.get_provenance_label(),
                is_road_distance=True,
                transit_mode=transit_mode or profile["transit_mode"],
                road_condition=profile["road_condition"],
                elevation_gain_m=profile["elevation_gain_m"],
                carbon_emissions_kg=profile["carbon_emissions_kg"],
                notes="Curated Himalayan mountain road corridor"
            )

        # Interpolated synthetic road corridor for other circuit pairs
        mid_lon = (lon1 + lon2) / 2.0 + 0.012  # Slight mountain curve
        mid_lat = (lat1 + lat2) / 2.0 - 0.008
        interpolated_waypoints = [
            [lon1, lat1],
            [lon1 * 0.7 + mid_lon * 0.3, lat1 * 0.7 + mid_lat * 0.3],
            [mid_lon, mid_lat],
            [mid_lon * 0.3 + lon2 * 0.7, mid_lat * 0.3 + lat2 * 0.7],
            [lon2, lat2],
        ]
        # Approximate distance from coordinate span
        from app.services.alternative_engine import haversine_distance_km
        approx_km = round(haversine_distance_km(lat1, lon1, lat2, lon2) * 1.45, 1)
        approx_duration = int(round(approx_km * 2.1))

        return RouteCalculationResponse(
            origin_destination_id=norm_orig,
            origin_name=CIRCUIT_NAMES[norm_orig],
            destination_destination_id=norm_dest,
            destination_name=CIRCUIT_NAMES[norm_dest],
            distance_km=approx_km,
            duration_minutes=approx_duration,
            route_geometry=RouteGeometry(coordinates=interpolated_waypoints),
            provider="demo",
            provenance_label=self.get_provenance_label(),
            is_road_distance=True,
            transit_mode=transit_mode or "Shared Himalayan Mountain Jeep",
            road_condition="Paved hill highway with winding turns and seasonal drainage",
            elevation_gain_m=500,
            carbon_emissions_kg=round(approx_km * 0.08, 2),
            notes="Interpolated synthetic mountain road corridor"
        )
