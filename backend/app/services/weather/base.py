"""
Base Weather Provider Interface for Yatri Setu.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from app.services.weather.schemas import WeatherObservation


class BaseWeatherProvider(ABC):
    """Abstract base class for all weather providers (Demo, OpenWeather, etc.)."""

    @abstractmethod
    def fetch_current(self, destination_id: str) -> WeatherObservation:
        """Fetch current weather observation for a destination."""
        pass

    @abstractmethod
    def fetch_forecast(self, destination_id: str, days: int = 7) -> List[WeatherObservation]:
        """Fetch multi-day forecast observations for a destination."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass

    @abstractmethod
    def get_provider_mode(self) -> str:
        """Returns provider mode: REAL, DEMO, or UNAVAILABLE."""
        pass
