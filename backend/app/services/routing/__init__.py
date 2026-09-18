"""
Routing package for Yatri Setu (Milestone 8A).
"""

from app.services.routing.schemas import RouteCalculationResponse, RouteGeometry
from app.services.routing.base import BaseRoutingProvider
from app.services.routing.service import routing_service, RoutingService
from app.services.routing.demo_provider import DemoRouteProvider
from app.services.routing.fallback_provider import FallbackRouteProvider
from app.services.routing.osrm_provider import OSRMRouteProvider
from app.services.routing.coordinates import CIRCUIT_COORDINATES, CIRCUIT_NAMES

__all__ = [
    "RouteCalculationResponse",
    "RouteGeometry",
    "BaseRoutingProvider",
    "routing_service",
    "RoutingService",
    "DemoRouteProvider",
    "FallbackRouteProvider",
    "OSRMRouteProvider",
    "CIRCUIT_COORDINATES",
    "CIRCUIT_NAMES",
]
