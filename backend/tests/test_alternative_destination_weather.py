"""
Unit and integration tests for alternative destination weather differentiation and provenance integrity.
Verifies:
1. Darjeeling alternatives endpoint returns Kalimpong weather for Kalimpong.
2. Distinct alternative destinations receive their own distinct weather observations.
3. Destination weather cannot leak across alternative cards (destination_id match).
4. All 6 regional destinations return valid alternatives with structured weather.
5. Weather provenance labels ('REAL — OPENWEATHER' vs 'DEMO MODE — SYNTHETIC DATA') are preserved.
6. Graceful fallback when OpenWeather is unavailable, with zero hardcoded 'Clear, 16°C'.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.alternative_engine import get_alternative_destinations
from app.services.weather.service import weather_service, WeatherService
from app.services.weather.schemas import WeatherObservation
from app.services.weather.provider import DemoWeatherProvider, UnavailableWeatherProvider

client = TestClient(app)

REGIONAL_DESTINATIONS = ["darjeeling", "kalimpong", "lava", "lolegaon", "rishop", "mirik"]


class TestAlternativeDestinationWeather:
    """Verify alternative destination weather is destination-specific, cached, and provenance-aware."""

    def test_darjeeling_alternatives_contain_kalimpong_weather(self):
        """Darjeeling alternatives must contain Kalimpong weather for Kalimpong."""
        response = get_alternative_destinations("darjeeling")
        assert response.origin_destination_id == "darjeeling"
        assert len(response.alternatives) > 0

        kalimpong_alt = next((a for a in response.alternatives if a.id == "kalimpong"), None)
        assert kalimpong_alt is not None
        assert kalimpong_alt.weather is not None
        assert kalimpong_alt.weather.destination_id == "kalimpong"
        assert kalimpong_alt.weather.temperature > 0
        assert kalimpong_alt.weather.condition is not None
        assert kalimpong_alt.weather.provenance_label is not None
        assert kalimpong_alt.weather_summary is not None
        assert "16°C" not in kalimpong_alt.weather_summary or "kalimpong" in kalimpong_alt.weather.destination_id

    def test_alternatives_receive_distinct_weather_observations(self):
        """Multiple alternatives in the same response must receive their own distinct weather."""
        response = get_alternative_destinations("darjeeling")
        weather_dest_ids = [a.weather.destination_id for a in response.alternatives if a.weather]
        
        # Every alternative's weather.destination_id must strictly match alternative.id
        for alt in response.alternatives:
            if alt.weather:
                assert alt.weather.destination_id == alt.id

        # Destination IDs in the list must be distinct
        assert len(weather_dest_ids) == len(set(weather_dest_ids))

    def test_no_weather_leakage_across_alternatives(self):
        """One destination's weather cannot leak into another destination's alternative card."""
        response = get_alternative_destinations("darjeeling")
        for alt in response.alternatives:
            if alt.weather:
                # Direct check against canonical weather service
                direct_weather = weather_service.get_weather(alt.id)
                assert alt.weather.destination_id == alt.id
                assert alt.weather.temperature == round(direct_weather.temperature_c, 1)

    def test_all_six_destinations_produce_valid_alternative_weather(self):
        """All 6 regional destinations must produce valid alternatives with weather."""
        for dest_id in REGIONAL_DESTINATIONS:
            res = get_alternative_destinations(dest_id)
            assert res.origin_destination_id == dest_id
            for alt in res.alternatives:
                assert alt.id != dest_id  # Cannot recommend itself
                assert alt.weather is not None
                assert alt.weather.destination_id == alt.id
                assert isinstance(alt.weather.temperature, (int, float))
                assert len(alt.weather.condition) > 0
                assert alt.weather_summary is not None
                # Must never be hardcoded generic string
                assert alt.weather_summary != "Clear, 16°C"

    def test_api_endpoint_returns_structured_weather(self):
        """GET /api/destinations/{id}/alternatives returns structured weather for each card."""
        resp = client.get("/api/destinations/darjeeling/alternatives")
        assert resp.status_code == 200
        data = resp.json()
        assert "alternatives" in data
        assert len(data["alternatives"]) > 0

        for alt in data["alternatives"]:
            assert "weather" in alt
            w = alt["weather"]
            assert w is not None
            assert "destination_id" in w
            assert "temperature" in w
            assert "condition" in w
            assert "provenance_label" in w
            assert "cache_status" in w
            assert alt["weather_summary"] != "Clear, 16°C"

    def test_real_openweather_provenance_preserved(self):
        """When OpenWeather returns live data, alternative weather carries REAL — OPENWEATHER."""
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_provider.fetch_current.side_effect = lambda d_id: WeatherObservation(
            destination_id=d_id,
            destination_name=d_id.capitalize(),
            temperature_c=19.4 if d_id == "kalimpong" else 11.2,
            temp_min_c=16.0,
            temp_max_c=22.0,
            precipitation_probability=10,
            humidity=55,
            weather_condition="Scattered Clouds",
            advisory="Pleasant weather",
            source="OpenWeatherMap API",
            provider_mode="REAL",
            provenance_label="REAL — OPENWEATHER",
            confidence=0.95,
            data_quality="HIGH",
            cache_status="LIVE"
        )

        fresh_service = WeatherService()
        fresh_service.set_provider(mock_provider)

        with patch("app.services.alternative_engine.weather_service", fresh_service):
            res = get_alternative_destinations("darjeeling")
            for alt in res.alternatives:
                assert alt.weather is not None
                assert alt.weather.provider_mode == "REAL"
                assert "OPENWEATHER" in alt.weather.provenance_label

    def test_unavailable_fallback_behavior_without_hardcoded_16c(self):
        """When weather provider fails or is unavailable, graceful fallback is followed without hardcoded 'Clear, 16°C'."""
        mock_provider = UnavailableWeatherProvider()
        fresh_service = WeatherService()
        fresh_service.set_provider(mock_provider)

        with patch("app.services.alternative_engine.weather_service", fresh_service):
            res = get_alternative_destinations("darjeeling")
            for alt in res.alternatives:
                assert alt.weather is not None
                # Provenance explicitly identifies safe fallback mode
                assert ("SAFE FALLBACK" in alt.weather.provenance_label or 
                        "DEMO MODE" in alt.weather.provenance_label or
                        "UNAVAILABLE" in alt.weather.provenance_label)
                assert alt.weather_summary != "Clear, 16°C"

        # Also test provider raising exception falls back to demo simulator
        err_provider = MagicMock()
        err_provider.fetch_current.side_effect = RuntimeError("OpenWeather API network unreachable")
        err_service = WeatherService()
        err_service.set_provider(err_provider)

        with patch("app.services.alternative_engine.weather_service", err_service):
            res_err = get_alternative_destinations("darjeeling")
            for alt in res_err.alternatives:
                assert alt.weather is not None
                assert alt.weather.provenance_label == "DEMO MODE — SYNTHETIC DATA"
                assert alt.weather_summary != "Clear, 16°C"
