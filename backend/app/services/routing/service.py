"""
Routing Coordinator Service for Yatri Setu (Milestone 8A).
Manages provider selection, automatic fallback cascade (OSRM -> Demo -> Haversine),
in-memory caching, and enrichment with traffic condition signals.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Tuple

from app.core.config import settings
from app.services.routing.base import BaseRoutingProvider
from app.services.routing.osrm_provider import OSRMRouteProvider
from app.services.routing.demo_provider import DemoRouteProvider
from app.services.routing.fallback_provider import FallbackRouteProvider
from app.services.routing.schemas import RouteCalculationResponse
from app.services.routing.coordinates import CIRCUIT_COORDINATES

logger = logging.getLogger(__name__)

DEFAULT_ROUTING_CACHE_TTL_SECONDS = 600  # 10 minutes


class RoutingService:
    """
    Provider-agnostic routing manager with automatic fallback and caching.
    Ensures that route visualization never crashes the frontend.
    """

    def __init__(self, ttl_seconds: int = DEFAULT_ROUTING_CACHE_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[Tuple[str, str, Optional[str]], Dict[str, Any]] = {}
        self._demo_provider = DemoRouteProvider()
        self._fallback_provider = FallbackRouteProvider()
        self._provider: BaseRoutingProvider = self._initialize_provider()

    def _initialize_provider(self) -> BaseRoutingProvider:
        mode = (getattr(settings, "ROUTING_PROVIDER", None) or "demo").lower().strip()
        if mode == "osrm":
            return OSRMRouteProvider()
        elif mode == "fallback":
            return self._fallback_provider
        return self._demo_provider

    def set_provider(self, provider: BaseRoutingProvider):
        """Allows runtime or test provider swapping."""
        self._provider = provider

    def get_provider_mode(self) -> str:
        """Returns the current active provider mode."""
        return self._provider.get_provider_name()

    def is_available(self) -> bool:
        """Returns True if the current provider is operational."""
        return self._provider.is_available()

    def calculate_route(
        self,
        origin_id: str,
        destination_id: str,
        transit_mode: Optional[str] = None,
        force_refresh: bool = False
    ) -> RouteCalculationResponse:
        """
        Calculates road route between origin and destination with caching.
        Falls back smoothly: OSRM -> Demo -> Fallback (Haversine).
        """
        norm_orig = origin_id.lower().strip()
        norm_dest = destination_id.lower().strip()

        if norm_orig not in CIRCUIT_COORDINATES:
            raise ValueError(f"Unknown origin destination: '{origin_id}'")
        if norm_dest not in CIRCUIT_COORDINATES:
            raise ValueError(f"Unknown destination: '{destination_id}'")

        cache_key = (norm_orig, norm_dest, transit_mode)
        now = datetime.utcnow()

        # Check cache
        if not force_refresh and cache_key in self._cache:
            cached = self._cache[cache_key]
            if now < cached["expires_at"]:
                return cached["response"].model_copy()

        response: Optional[RouteCalculationResponse] = None

        # Attempt primary provider
        try:
            response = self._provider.calculate_route(norm_orig, norm_dest, transit_mode)
        except Exception as ex:
            logger.warning(
                f"Primary routing provider '{self._provider.get_provider_name()}' failed for "
                f"'{norm_orig}' -> '{norm_dest}': {ex}. Falling back to demo/haversine."
            )
            # Try demo provider if primary was not demo
            if self._provider.get_provider_name() != "demo":
                try:
                    response = self._demo_provider.calculate_route(norm_orig, norm_dest, transit_mode)
                    response.notes = "Fallback from live routing provider to synthetic mountain corridor"
                except Exception as ex_demo:
                    logger.warning(f"Demo routing also failed: {ex_demo}. Using Haversine fallback.")

            # Final safety net: Haversine straight-line fallback
            if response is None:
                response = self._fallback_provider.calculate_route(norm_orig, norm_dest, transit_mode)

        # Enrich with live traffic condition if available from M7C traffic service
        try:
            from app.services.traffic.service import traffic_service
            traffic_summary = traffic_service.get_traffic(norm_dest)
            if traffic_summary:
                response.traffic_condition = f"{traffic_summary.corridor_traffic_level} ({traffic_summary.access_status})"
        except Exception:
            pass

        # Cache response
        self._cache[cache_key] = {
            "response": response,
            "expires_at": now + timedelta(seconds=self.ttl_seconds)
        }

        return response


# Singleton Instance
routing_service = RoutingService()
