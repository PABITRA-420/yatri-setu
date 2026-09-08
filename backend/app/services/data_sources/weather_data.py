"""
Weather Data Provider for Yatri Setu.
Translates Himalayan meteorological conditions (visibility, precipitation, road hazard risk)
into normalized destination weather pressure.
"""
from typing import Optional
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading
from app.services.weather_service import get_destination_weather


from app.services.data_sources.weather_real_provider import WeatherProviderAdapter

class MockWeatherDataProvider(WeatherProviderAdapter):
    """
    Backwards-compatible alias for WeatherProviderAdapter.
    Supports MOCK mode (default), REAL OpenWeather mode, and CACHED mode.
    """
    pass


weather_data_provider = WeatherProviderAdapter()

