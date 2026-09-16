"""
Traffic Service Package for Yatri Setu (Milestone 7C).
"""

from app.services.traffic.schemas import (
    RouteTrafficObservation,
    DestinationTrafficSummary,
    TrafficImpactSignal
)
from app.services.traffic.base import BaseTrafficProvider
from app.services.traffic.provider import (
    DemoTrafficProvider,
    RealTrafficProvider,
    UnavailableTrafficProvider
)
from app.services.traffic.service import TrafficService, traffic_service

__all__ = [
    "RouteTrafficObservation",
    "DestinationTrafficSummary",
    "TrafficImpactSignal",
    "BaseTrafficProvider",
    "DemoTrafficProvider",
    "RealTrafficProvider",
    "UnavailableTrafficProvider",
    "TrafficService",
    "traffic_service"
]
