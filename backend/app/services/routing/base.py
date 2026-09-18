"""
Base Routing Provider Interface for Yatri Setu (Milestone 8A).
"""

from abc import ABC, abstractmethod
from typing import Optional
from app.services.routing.schemas import RouteCalculationResponse


class BaseRoutingProvider(ABC):
    """Abstract base class for all Yatri Setu routing providers."""

    @abstractmethod
    def calculate_route(
        self,
        origin_id: str,
        destination_id: str,
        transit_mode: Optional[str] = None
    ) -> RouteCalculationResponse:
        """
        Calculates or estimates road route between two circuit destinations.
        Raises ValueError if destination is unknown or calculation impossible.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is operational and configured."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns provider identifier: 'osrm', 'demo', or 'fallback'."""
        pass

    @abstractmethod
    def get_provenance_label(self) -> str:
        """Returns provenance tag for reporting and UI badges."""
        pass
