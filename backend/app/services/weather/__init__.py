"""
Weather Service Package for Yatri Setu (Milestone 7C).
"""

from app.services.weather.schemas import WeatherObservation, WeatherImpactSignal
from app.services.weather.base import BaseWeatherProvider
from app.services.weather.provider import (
    DemoWeatherProvider,
    OpenWeatherProvider,
    UnavailableWeatherProvider
)
from app.services.weather.service import WeatherService, weather_service

__all__ = [
    "WeatherObservation",
    "WeatherImpactSignal",
    "BaseWeatherProvider",
    "DemoWeatherProvider",
    "OpenWeatherProvider",
    "UnavailableWeatherProvider",
    "WeatherService",
    "weather_service"
]
