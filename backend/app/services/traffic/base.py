"""
Base Traffic Provider Interface for Yatri Setu.
"""

from abc import ABC, abstractmethod
from app.services.traffic.schemas import DestinationTrafficSummary


class BaseTrafficProvider(ABC):
    """Abstract base class for arterial mountain traffic providers."""

    @abstractmethod
    def fetch_traffic(self, destination_id: str) -> DestinationTrafficSummary:
        """Fetch arterial traffic and corridor accessibility for a destination."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass

    @abstractmethod
    def get_provider_mode(self) -> str:
        """Returns provider mode: REAL, DEMO, or UNAVAILABLE."""
        pass
