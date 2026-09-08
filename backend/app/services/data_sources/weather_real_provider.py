"""
OpenWeather Real Provider Adapter with graceful mock fallback and TTL caching.
Adheres strictly to the rule: NEVER label MOCK or CACHED data as LIVE.
"""

import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import httpx

from app.core.config import settings
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading
from app.services.weather_service import get_destination_weather

logger = logging.getLogger(__name__)

# Destination coordinates for OpenWeather queries
DESTINATION_COORDINATES: Dict[str, Tuple[float, float]] = {
    "darjeeling": (27.0410, 88.2663),
    "kalimpong": (27.0594, 88.4695),
    "lava": (27.0864, 88.6603),
    "lolegaon": (27.0142, 88.5583),
    "rishop": (27.1065, 88.6496),
    "mirik": (26.9011, 88.1755),
}

CACHE_TTL_SECONDS = 900  # 15 minutes cache


class WeatherProviderAdapter(BaseDataSourceProvider):
    """
    Dual-mode Weather Provider:
    - If WEATHER_PROVIDER == 'openweather' and OPENWEATHER_API_KEY is present:
        Attempts real OpenWeather API call.
        Uses TTL cache (marked as CACHED).
        On error, safely degrades to MOCK without crashing.
    - Otherwise:
        Runs in deterministic MOCK mode.
    """
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    @property
    def is_configured_real(self) -> bool:
        return (
            settings.WEATHER_PROVIDER.lower() == "openweather" and
            bool(settings.OPENWEATHER_API_KEY and settings.OPENWEATHER_API_KEY.strip())
        )

    def get_mode(self) -> str:
        if self.is_configured_real:
            return "REAL"
        return "MOCK"

    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        normalized_id = destination_id.lower().strip()

        # 1. If configured for OpenWeather, attempt real API or return cached
        if self.is_configured_real:
            try:
                # Check cache first
                now = time.time()
                cached = self._cache.get(normalized_id)
                if cached and (now - cached["timestamp"]) < CACHE_TTL_SECONDS:
                    return DataSourceReading(
                        value=cached["value"],
                        available=True,
                        source="CACHED_OPENWEATHERMAP",
                        confidence=0.92,
                        raw_value=cached["raw_value"],
                        unit="celsius",
                        provider_mode="CACHED",
                        data_quality="HIGH",
                        signal_type="WEATHER",
                        notes=f"Cached real weather: {cached['condition']}, {cached['temp_c']}°C (TTL: {int(CACHE_TTL_SECONDS - (now - cached['timestamp']))}s remaining)"
                    )

                # Fetch real weather
                coords = DESTINATION_COORDINATES.get(normalized_id, (27.0410, 88.2663))
                lat, lon = coords
                url = (
                    f"https://api.openweathermap.org/data/2.5/weather"
                    f"?lat={lat}&lon={lon}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
                )

                with httpx.Client(timeout=4.0) as client:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        temp = float(data.get("main", {}).get("temp", 15.0))
                        humidity = float(data.get("main", {}).get("humidity", 60.0))
                        weather_desc = data.get("weather", [{}])[0].get("description", "Clear").title()

                        # Calculate pressure favorability: 18-24°C with low humidity = 85 (high influx demand)
                        # Harsh freezing or heavy monsoon = low pressure
                        comfort = max(10.0, min(100.0, 100.0 - abs(temp - 20.0) * 3.0 - (humidity * 0.2)))

                        # Store in cache
                        self._cache[normalized_id] = {
                            "timestamp": now,
                            "value": round(comfort, 1),
                            "raw_value": temp,
                            "condition": weather_desc,
                            "temp_c": temp
                        }

                        return DataSourceReading(
                            value=round(comfort, 1),
                            available=True,
                            source="LIVE_OPENWEATHERMAP_API",
                            confidence=0.98,
                            raw_value=temp,
                            unit="celsius",
                            provider_mode="REAL",
                            data_quality="HIGH",
                            signal_type="WEATHER",
                            notes=f"Live observation: {weather_desc}, {temp}°C, Humidity {humidity}%"
                        )
                    else:
                        logger.warning(f"OpenWeather returned HTTP {resp.status_code}, falling back to mock.")
            except Exception as e:
                logger.warning(f"Failed to fetch OpenWeather real reading ({e}), gracefully falling back to mock.")

        # 2. Deterministic Mock Fallback (when no key or API unavailable)
        forecast = get_destination_weather(normalized_id)
        if not forecast:
            return self.get_unavailable_reading("Weather profile not found")

        vis_score = float(forecast.mountain_visibility_score)
        rain_penalty = 25.0 if forecast.rain_expected else 0.0
        precip_penalty = forecast.precipitation_chance_percent * 0.25
        weather_pressure = max(10.0, min(100.0, vis_score * 0.9 - rain_penalty - precip_penalty + 15.0))

        return DataSourceReading(
            value=round(weather_pressure, 1),
            available=True,
            source="MOCK_METEOROLOGICAL_SIMULATOR",
            confidence=0.90,
            raw_value=float(forecast.precipitation_chance_percent),
            unit="precip_chance_percent",
            provider_mode="MOCK",
            data_quality="HIGH",
            signal_type="WEATHER",
            notes=f"Deterministic fallback: {forecast.condition} | Visibility: {forecast.mountain_visibility_score}/100"
        )
