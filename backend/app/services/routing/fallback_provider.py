"""
Fallback Routing Provider using Haversine straight-line distance calculation.
Used when road routing network is unreachable or offline.
"""

from typing import Optional
from app.services.routing.base import BaseRoutingProvider
from app.services.routing.schemas import RouteCalculationResponse, RouteGeometry
from app.services.routing.coordinates import CIRCUIT_COORDINATES, CIRCUIT_NAMES
from app.services.alternative_engine import haversine_distance_km


class FallbackRouteProvider(BaseRoutingProvider):
    """
    Computes straight-line Haversine geographic estimate when road routing is unavailable.
    Explicitly flags is_road_distance=False to prevent misleading travel times.
    """

    def is_available(self) -> bool:
        return True

    def get_provider_name(self) -> str:
        return "fallback"

    def get_provenance_label(self) -> str:
        return "FALLBACK — ROUTING UNAVAILABLE (HAVERSINE GEOGRAPHIC ESTIMATE)"

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

        distance_km = haversine_distance_km(lat1, lon1, lat2, lon2)
        # Approximate mountain travel duration: straight-line distance scaled by 1.8 winding factor @ 30 km/h
        est_duration = max(10, int(round((distance_km * 1.8 / 30.0) * 60))) if norm_orig != norm_dest else 15

        geometry = RouteGeometry(
            coordinates=[
                [lon1, lat1],
                [lon2, lat2]
            ]
        )

        return RouteCalculationResponse(
            origin_destination_id=norm_orig,
            origin_name=CIRCUIT_NAMES.get(norm_orig, norm_orig.title()),
            destination_destination_id=norm_dest,
            destination_name=CIRCUIT_NAMES.get(norm_dest, norm_dest.title()),
            distance_km=distance_km,
            duration_minutes=est_duration,
            route_geometry=geometry,
            provider="fallback",
            provenance_label=self.get_provenance_label(),
            is_road_distance=False,
            transit_mode=transit_mode or "Geographic Proximity Estimate",
            road_condition="Road network data unavailable; straight-line geographic estimate displayed",
            elevation_gain_m=0,
            carbon_emissions_kg=0.0,
            notes="Approximate straight-line geographic distance (Haversine). Road routing unavailable."
        )
