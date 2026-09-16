"""
Weather Service for Yatri Setu (Milestone 7C).
Manages provider selection, TTL caching, stale fallbacks, and deterministic weather impact calculation.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import time

from app.core.config import settings
from app.services.weather.base import BaseWeatherProvider
from app.services.weather.provider import (
    DemoWeatherProvider,
    OpenWeatherProvider,
    UnavailableWeatherProvider
)
from app.services.weather.schemas import WeatherObservation, WeatherImpactSignal

logger = logging.getLogger(__name__)

DEFAULT_WEATHER_TTL_SECONDS = 900  # 15 minutes


class WeatherService:
    """
    Provider-agnostic weather coordinator with strict provenance,
    in-memory TTL cache, stale fallback resilience, and deterministic impact modeling.
    """

    def __init__(self, ttl_seconds: int = DEFAULT_WEATHER_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._provider: BaseWeatherProvider = self._initialize_provider()

    def _initialize_provider(self) -> BaseWeatherProvider:
        mode = (settings.WEATHER_PROVIDER or "demo").lower().strip()
        if mode == "openweather":
            openweather = OpenWeatherProvider()
            if openweather.is_available():
                return openweather
            logger.info("OpenWeather API key missing; falling back to DemoWeatherProvider")
            return DemoWeatherProvider()
        elif mode == "unavailable":
            return UnavailableWeatherProvider()
        return DemoWeatherProvider()

    def set_provider(self, provider: BaseWeatherProvider):
        """Allows runtime or test provider swapping."""
        self._provider = provider

    def get_weather(self, destination_id: str, force_refresh: bool = False) -> WeatherObservation:
        """
        Retrieves current weather observation for a destination with caching.
        Employs graceful fallback: if provider fails, returns stale cache or demo fallback.
        """
        dest_clean = destination_id.lower().strip()
        now = datetime.utcnow()
        cached_entry = self._cache.get(dest_clean)

        # Check valid unexpired cache
        if not force_refresh and cached_entry:
            expires_at = cached_entry["expires_at"]
            if now < expires_at:
                obs: WeatherObservation = cached_entry["observation"].model_copy()
                obs.cache_status = "CACHED"
                obs.expires_at = expires_at
                return obs

        # Fetch fresh observation from provider
        try:
            fresh_obs = self._provider.fetch_current(dest_clean)
            expires_at = now + timedelta(seconds=self.ttl_seconds)
            fresh_obs.expires_at = expires_at
            fresh_obs.cache_status = "LIVE"

            self._cache[dest_clean] = {
                "observation": fresh_obs,
                "expires_at": expires_at,
                "cached_at": now
            }
            return fresh_obs

        except Exception as ex:
            logger.warning(f"Weather provider error for {dest_clean}: {ex}. Checking stale cache fallback.")
            # If stale cache exists, return it tagged as STALE
            if cached_entry:
                stale_obs: WeatherObservation = cached_entry["observation"].model_copy()
                stale_obs.cache_status = "STALE"
                stale_obs.data_quality = "DEGRADED"
                stale_obs.confidence = max(0.4, stale_obs.confidence * 0.7)
                stale_obs.advisory += " [Notice: Displaying cached observation due to temporary telemetry delay]"
                return stale_obs

            # Otherwise, fall back to safe demo simulator
            demo = DemoWeatherProvider()
            fallback_obs = demo.fetch_current(dest_clean)
            fallback_obs.cache_status = "STALE"
            fallback_obs.data_quality = "DEGRADED"
            fallback_obs.confidence = 0.50
            return fallback_obs

    def get_forecast(self, destination_id: str, days: int = 7) -> List[WeatherObservation]:
        """Fetches multi-day weather forecast observations."""
        dest_clean = destination_id.lower().strip()
        try:
            return self._provider.fetch_forecast(dest_clean, days)
        except Exception as ex:
            logger.warning(f"Forecast fetch failed for {dest_clean}: {ex}. Using demo forecast generator.")
            demo = DemoWeatherProvider()
            return demo.fetch_forecast(dest_clean, days)

    def calculate_weather_impact(self, obs: WeatherObservation) -> WeatherImpactSignal:
        """
        Deterministic, explainable weather impact factor.
        Weather impact ∈ [-1.0, +1.0]:
        - Pleasant mountain climate -> +0.1 to +0.2 (modest positive demand boost)
        - Light rain / mist -> -0.1 to -0.3 (mild outdoor dampening)
        - Heavy rain (>15mm) -> -0.6 to -0.8 (substantial outdoor deterrence)
        - Severe storm / landslide alert -> -1.0 (safety override)
        """
        temp = obs.temperature_c
        rain_mm = obs.precipitation_mm
        prob = obs.precipitation_probability
        wind = obs.wind_speed_kmh
        severe = obs.severe_weather

        # 1. Severe Weather Override
        if severe or "warning" in obs.weather_condition.lower() or "landslide" in obs.weather_condition.lower():
            return WeatherImpactSignal(
                destination_id=obs.destination_id,
                weather_impact=-1.0,
                impact_factor=10.0,  # Extreme dampening on regular tourism flow
                advisory_level="CRITICAL",
                tourism_suitability="HAZARDOUS",
                description=f"Severe Meteorological Warning: {severe or obs.weather_condition}. Travel not advised.",
                confidence=obs.confidence,
                source=obs.source,
                provider_mode=obs.provider_mode,
                observed_at=obs.observed_at
            )

        # 2. Temperature factor (-0.3 to +0.2)
        # Optimal mountain range: 16°C - 22°C
        if 16.0 <= temp <= 22.0:
            temp_impact = 0.15
        elif 12.0 <= temp < 16.0 or 22.0 < temp <= 26.0:
            temp_impact = 0.05
        elif 8.0 <= temp < 12.0:
            temp_impact = -0.10
        elif temp < 8.0:
            temp_impact = -0.25  # Bitter cold
        else:
            temp_impact = -0.20  # Overheating

        # 3. Precipitation factor (-0.7 to 0.0)
        if rain_mm > 25.0 or prob >= 85:
            rain_impact = -0.75
            suitability = "POOR"
            advisory = "WARNING"
            rain_desc = f"Heavy torrential mountain rainfall ({rain_mm:.1f}mm). Outdoor activities severely restricted."
        elif rain_mm > 10.0 or prob >= 60:
            rain_impact = -0.45
            suitability = "MODERATE"
            advisory = "ADVISORY"
            rain_desc = f"Steady rain expected ({rain_mm:.1f}mm). Sightseeing trails slippery; covered attractions recommended."
        elif rain_mm > 2.0 or prob >= 40:
            rain_impact = -0.20
            suitability = "GOOD"
            advisory = "NORMAL"
            rain_desc = "Intermittent mountain mist or drizzle. Bring light rain gear."
        else:
            rain_impact = 0.05
            suitability = "EXCELLENT" if temp_impact > 0 else "GOOD"
            advisory = "NORMAL"
            rain_desc = "Clear and dry mountain conditions favorable for panoramic views and forest hikes."

        # 4. Wind penalty
        wind_impact = -0.10 if wind > 40.0 else 0.0

        # Combine
        total_impact = max(-1.0, min(1.0, round(temp_impact + rain_impact + wind_impact, 2)))

        # Convert to 0-100 impact factor for pressure aggregation
        # -1.0 -> 10, 0.0 -> 50, +1.0 -> 85
        impact_factor = round(50.0 + (total_impact * 35.0), 1)

        full_desc = f"{rain_desc} Temp: {temp:.1f}°C, Wind: {wind:.0f} km/h."

        return WeatherImpactSignal(
            destination_id=obs.destination_id,
            weather_impact=total_impact,
            impact_factor=impact_factor,
            advisory_level=advisory,
            tourism_suitability=suitability,
            description=full_desc,
            confidence=obs.confidence,
            source=obs.source,
            provider_mode=obs.provider_mode,
            observed_at=obs.observed_at
        )

    def get_weather_impact(self, destination_id: str) -> WeatherImpactSignal:
        """Helper to get current weather and compute its impact signal in one step."""
        obs = self.get_weather(destination_id)
        return self.calculate_weather_impact(obs)


# Global Singleton Instance
weather_service = WeatherService()
