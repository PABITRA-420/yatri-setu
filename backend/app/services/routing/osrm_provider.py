"""
OSRM Routing Provider for Yatri Setu (Milestone 8A).
Queries OpenStreetMap-compatible OSRM public routing API for actual road distance and geometry.
"""

import json
import logging
import urllib.request
from typing import Optional
from app.services.routing.base import BaseRoutingProvider
from app.services.routing.schemas import RouteCalculationResponse, RouteGeometry
from app.services.routing.coordinates import CIRCUIT_COORDINATES, CIRCUIT_NAMES

logger = logging.getLogger(__name__)

OSRM_BASE_URL = "https://router.project-osrm.org/route/v1/driving"
OSRM_TIMEOUT_SECONDS = 3.5


class OSRMRouteProvider(BaseRoutingProvider):
    """
    OpenStreetMap-compatible road routing provider using public OSRM.
    Requires no API keys; includes strict timeouts and structured error handling.
    """

    def __init__(self, base_url: str = OSRM_BASE_URL, timeout_seconds: float = OSRM_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> bool:
        return True

    def get_provider_name(self) -> str:
        return "osrm"

    def get_provenance_label(self) -> str:
        return "REAL — OSRM (OPENSTREETMAP)"

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

        # Construct OSRM request URL
        url = f"{self.base_url}/{lon1:.6f},{lat1:.6f};{lon2:.6f},{lat2:.6f}?overview=full&geometries=geojson"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "YatriSetu-HimalayanRouter/1.0 (Hackathon Prototype)"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                if resp.status != 200:
                    raise IOError(f"OSRM returned HTTP status {resp.status}")
                data = json.loads(resp.read().decode("utf-8"))

            if data.get("code") != "Ok" or not data.get("routes"):
                raise IOError(f"OSRM returned non-success code: {data.get('code')}")

            best_route = data["routes"][0]
            distance_meters = best_route.get("distance", 0.0)
            duration_seconds = best_route.get("duration", 0.0)
            geometry_data = best_route.get("geometry", {})
            coordinates = geometry_data.get("coordinates", [])

            if not coordinates:
                raise IOError("OSRM returned empty geometry coordinates")

            distance_km = round(distance_meters / 1000.0, 1)
            duration_minutes = max(1, int(round(duration_seconds / 60.0)))

            return RouteCalculationResponse(
                origin_destination_id=norm_orig,
                origin_name=CIRCUIT_NAMES[norm_orig],
                destination_destination_id=norm_dest,
                destination_name=CIRCUIT_NAMES[norm_dest],
                distance_km=distance_km,
                duration_minutes=duration_minutes,
                route_geometry=RouteGeometry(coordinates=coordinates),
                provider="osrm",
                provenance_label=self.get_provenance_label(),
                is_road_distance=True,
                transit_mode=transit_mode or "Shared Himalayan Jeep / Mountain Vehicle",
                road_condition="OpenStreetMap active road artery",
                elevation_gain_m=0,
                carbon_emissions_kg=round(distance_km * 0.08, 2),
                notes="Live road routing retrieved via OpenStreetMap OSRM engine"
            )

        except Exception as e:
            logger.warning(f"OSRM route calculation failed ({norm_orig} -> {norm_dest}): {e}")
            raise
