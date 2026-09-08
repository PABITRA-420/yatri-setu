"""
Weather Ingestor (Milestone 6B).

Bridges the existing WeatherProviderAdapter into the normalized IngestedObservation schema.
Supports REAL (OpenWeather API) and MOCK modes transparently.

Real mode requires: WEATHER_PROVIDER=openweather and OPENWEATHER_API_KEY set in environment.
Otherwise operates in deterministic MOCK mode — never silently misrepresenting the source.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.services.ingestion.base_ingestor import (
    BaseIngestor, IngestedObservation, ProviderMode
)
from app.services.data_sources.weather_real_provider import WeatherProviderAdapter

logger = logging.getLogger(__name__)

# Reuse the singleton adapter already used by CrowdEngineV2
_weather_adapter = WeatherProviderAdapter()


class WeatherIngestor(BaseIngestor):
    """
    Ingests weather pressure signal per destination.

    Output signal: weather_pressure (0–100 normalized crowd-attractiveness score).
    Real mode: Uses OpenWeather API (with 15-min TTL cache, marked CACHED when served from cache).
    Mock mode: Deterministic meteorological simulation (marked MOCK).

    Additional raw fields stored: temperature (°C), precipitation_chance (%).
    """

    @property
    def source_label(self) -> str:
        return "OpenWeatherMap" if _weather_adapter.is_configured_real else "Mock Meteorological Simulator"

    @property
    def signal_name(self) -> str:
        return "weather_pressure"

    @property
    def provider_mode(self) -> ProviderMode:
        if _weather_adapter.is_configured_real:
            return ProviderMode.REAL
        return ProviderMode.MOCK

    def _fetch_real(self, destination_id: str, date: str) -> IngestedObservation:
        reading = _weather_adapter.get_reading(destination_id, date)
        # Map the adapter's provider_mode string to our enum
        mode_str = getattr(reading, "provider_mode", "REAL")
        try:
            obs_mode = ProviderMode(mode_str)
        except ValueError:
            obs_mode = ProviderMode.REAL

        return IngestedObservation(
            destination_id=destination_id.lower().strip(),
            date=date,
            signal_name=self.signal_name,
            signal_value=round(float(reading.value), 1),
            raw_value=reading.raw_value,
            raw_unit=reading.unit,
            source=reading.source,
            provider_mode=obs_mode,
            timestamp=datetime.now(timezone.utc),
            confidence=reading.confidence,
            data_quality=reading.data_quality,
            notes=reading.notes,
        )

    def _fetch_mock(self, destination_id: str, date: str) -> IngestedObservation:
        reading = _weather_adapter.get_reading(destination_id, date)
        return IngestedObservation(
            destination_id=destination_id.lower().strip(),
            date=date,
            signal_name=self.signal_name,
            signal_value=round(float(reading.value), 1),
            raw_value=reading.raw_value,
            raw_unit=reading.unit,
            source="Mock Meteorological Simulator",
            provider_mode=ProviderMode.MOCK,
            timestamp=datetime.now(timezone.utc),
            confidence=reading.confidence,
            data_quality=reading.data_quality,
            notes=reading.notes,
        )


weather_ingestor = WeatherIngestor()
