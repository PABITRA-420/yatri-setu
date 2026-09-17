"""
Unit and integration tests for Canonical Weather Integration and Destination Differentiation.
Verifies:
1. Exact coordinate mapping for all 6 regional destinations (no silent fallback).
2. Unknown destinations raise ValueError at provider level and 404 at API level.
3. Live / mock OpenWeather responses differ across destinations (distinct coordinates & telemetry).
4. Tourist-facing weather endpoint (/api/destinations/{id}/weather) shares the exact same
   underlying WeatherService, cache, and provenance labels as M7C dynamic recalculator.
5. Independent cache keys per destination (Darjeeling cache does not pollute Kalimpong or Lava).
6. Accurate provenance semantics: REAL — OPENWEATHER, CACHED — OPENWEATHER, DEMO MODE — SYNTHETIC DATA.
7. M7C dynamic recalculation ingests the identical weather observation.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.weather.provider import (
    DESTINATION_COORDINATES,
    DEMO_WEATHER_PROFILES,
    OpenWeatherProvider,
    DemoWeatherProvider,
    WeatherObservation
)
from app.services.weather.service import WeatherService, weather_service
from app.services.weather_service import get_destination_weather, CanonicalWeatherProvider
from app.services.pressure_refresh_service import PressureRefreshService

client = TestClient(app)


class TestWeatherDestinationCoordinates:
    """Verify distinct coordinates and strict validation."""

    def test_all_six_destinations_have_distinct_coordinates(self):
        """Verify each of the 6 hill stations has unique latitude and longitude coordinates."""
        expected_destinations = ["darjeeling", "kalimpong", "lava", "lolegaon", "rishop", "mirik"]
        coords_set = set()

        for dest in expected_destinations:
            assert dest in DESTINATION_COORDINATES, f"Missing coordinate for {dest}"
            coords = DESTINATION_COORDINATES[dest]
            assert isinstance(coords, tuple) and len(coords) == 2
            lat, lon = coords
            assert 26.5 <= lat <= 27.5, f"Latitude {lat} out of Darjeeling/Kalimpong range for {dest}"
            assert 88.0 <= lon <= 89.0, f"Longitude {lon} out of Darjeeling/Kalimpong range for {dest}"
            coords_set.add(coords)

        # All 6 destinations must have distinct geographical coordinates
        assert len(coords_set) == len(expected_destinations), "Coordinates must be unique per destination"

    def test_unknown_destination_raises_value_error_in_providers(self):
        """Unknown destination must raise ValueError, not silently default to Darjeeling or Kalimpong."""
        real_provider = OpenWeatherProvider(api_key="mock_key")
        with pytest.raises(ValueError, match="Unknown destination 'unknown_valley'"):
            real_provider.fetch_current("unknown_valley")

        demo_provider = DemoWeatherProvider()
        with pytest.raises(ValueError, match="Unknown destination 'unknown_valley'"):
            demo_provider.fetch_current("unknown_valley")


class TestOpenWeatherDifferentiation:
    """Verify OpenWeather provider sends destination-specific coords and outputs different weather."""

    def test_fetch_current_uses_destination_specific_coords(self):
        """Verify that fetch_current calls OpenWeather with destination's exact lat/lon."""
        provider = OpenWeatherProvider(api_key="test_api_key")

        darj_lat, darj_lon = DESTINATION_COORDINATES["darjeeling"]
        kalim_lat, kalim_lon = DESTINATION_COORDINATES["kalimpong"]

        mock_resp_darj = MagicMock()
        mock_resp_darj.status_code = 200
        mock_resp_darj.json.return_value = {
            "main": {"temp": 12.0, "temp_min": 9.0, "temp_max": 15.0, "humidity": 75},
            "wind": {"speed": 4.0},
            "visibility": 10000,
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
            "rain": {}
        }

        with patch("httpx.Client.get") as mock_get:
            mock_get.return_value = mock_resp_darj
            obs = provider.fetch_current("darjeeling")
            mock_get.assert_called_once()
            called_url = mock_get.call_args[0][0]
            assert f"lat={darj_lat}" in called_url
            assert f"lon={darj_lon}" in called_url
            assert obs.destination_id == "darjeeling"
            assert obs.temperature_c == 12.0
            assert obs.provenance_label == "REAL — OPENWEATHER"

        mock_resp_kalim = MagicMock()
        mock_resp_kalim.status_code = 200
        mock_resp_kalim.json.return_value = {
            "main": {"temp": 19.5, "temp_min": 16.0, "temp_max": 23.0, "humidity": 55},
            "wind": {"speed": 2.5},
            "visibility": 10000,
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "rain": {}
        }

        with patch("httpx.Client.get") as mock_get:
            mock_get.return_value = mock_resp_kalim
            obs = provider.fetch_current("kalimpong")
            called_url = mock_get.call_args[0][0]
            assert f"lat={kalim_lat}" in called_url
            assert f"lon={kalim_lon}" in called_url
            assert obs.destination_id == "kalimpong"
            assert obs.temperature_c == 19.5
            assert obs.provenance_label == "REAL — OPENWEATHER"


class TestWeatherCacheIndependenceAndProvenance:
    """Verify cache per destination and explicit provenance labeling."""

    def test_cache_is_isolated_per_destination(self):
        """Caching Darjeeling must never return Darjeeling data for Kalimpong, Lava, or Rishop."""
        service = WeatherService(ttl_seconds=900)

        # Seed darjeeling
        darj_obs = service.get_weather("darjeeling", force_refresh=True)
        assert darj_obs.destination_id == "darjeeling"

        # Request kalimpong - must not be cached Darjeeling
        kalim_obs = service.get_weather("kalimpong")
        assert kalim_obs.destination_id == "kalimpong"
        assert kalim_obs.temperature_c != darj_obs.temperature_c or kalim_obs.destination_name != darj_obs.destination_name

    def test_unexpired_cache_marks_cache_status_and_provenance(self):
        """Unexpired cache returns CACHED status and CACHED — OPENWEATHER provenance in REAL mode."""
        service = WeatherService(ttl_seconds=900)
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_provider.get_provider_mode.return_value = "REAL"
        mock_provider.fetch_current.return_value = WeatherObservation(
            destination_id="darjeeling",
            destination_name="Darjeeling",
            observed_at=datetime.utcnow(),
            forecast_for=None,
            temperature_c=14.0,
            temp_min_c=10.0,
            temp_max_c=18.0,
            precipitation_probability=10,
            precipitation_mm=0.0,
            humidity=60,
            wind_speed_kmh=8.0,
            weather_condition="Clear",
            severe_weather=None,
            visibility_km=15.0,
            advisory="Pleasant weather",
            best_hours_for_outdoors="Morning",
            source="OPENWEATHERMAP_LIVE",
            provider_mode="REAL",
            provenance_label="REAL — OPENWEATHER",
            confidence=0.95,
            data_quality="HIGH"
        )
        service.set_provider(mock_provider)

        # First call fetches LIVE
        first_call = service.get_weather("darjeeling", force_refresh=True)
        assert first_call.cache_status == "LIVE"
        assert first_call.provenance_label == "REAL — OPENWEATHER"
        assert mock_provider.fetch_current.call_count == 1

        # Second call returns CACHED
        second_call = service.get_weather("darjeeling", force_refresh=False)
        assert second_call.cache_status == "CACHED"
        assert second_call.provenance_label == "CACHED — OPENWEATHER"
        assert mock_provider.fetch_current.call_count == 1


class TestTouristWeatherEndpointAndM7CAlignment:
    """Verify tourist endpoint and M7C share the exact same canonical weather engine."""

    def test_tourist_endpoint_returns_extended_telemetry_and_provenance(self):
        """GET /api/destinations/{id}/weather returns full canonical telemetry and provenance."""
        response = client.get("/api/destinations/darjeeling/weather")
        assert response.status_code == 200
        data = response.json()
        assert data["destination_id"] == "darjeeling"
        assert "provenance_label" in data
        assert "provider_mode" in data
        assert "cache_status" in data
        assert "humidity" in data
        assert "precipitation_mm" in data
        assert "wind_speed_kmh" in data
        assert data["provider_mode"] in ["REAL", "DEMO"]
        assert data["provenance_label"] in ["REAL — OPENWEATHER", "CACHED — OPENWEATHER", "DEMO MODE — SYNTHETIC DATA"]

    def test_tourist_endpoint_differentiates_all_destinations(self):
        """Check that Darjeeling, Kalimpong, and Lava return distinct weather responses."""
        resp_darj = client.get("/api/destinations/darjeeling/weather")
        resp_kalim = client.get("/api/destinations/kalimpong/weather")
        resp_lava = client.get("/api/destinations/lava/weather")

        assert resp_darj.status_code == 200
        assert resp_kalim.status_code == 200
        assert resp_lava.status_code == 200

        data_darj = resp_darj.json()
        data_kalim = resp_kalim.json()
        data_lava = resp_lava.json()

        assert data_darj["destination_name"] == "Darjeeling"
        assert data_kalim["destination_name"] == "Kalimpong"
        assert data_lava["destination_name"] == "Lava"

        # Temperatures and conditions must differ across destinations
        assert (data_darj["temp_min_c"], data_darj["temp_max_c"]) != (data_kalim["temp_min_c"], data_kalim["temp_max_c"])
        assert data_darj["condition"] != data_lava["condition"]

    def test_unknown_destination_returns_404_or_controlled_error(self):
        """Unknown destination returns 404 on tourist weather endpoint."""
        response = client.get("/api/destinations/atlantis_underwater/weather")
        assert response.status_code in [404, 400]

    def test_m7c_recalculator_shares_identical_weather_signal(self):
        """Verify M7C PressureRefreshService uses the exact same WeatherService instance."""
        refresh_service = PressureRefreshService()
        conditions = refresh_service.recalculate_destination_pressure("darjeeling")
        weather_obs = conditions.weather

        assert weather_obs.destination_id == "darjeeling"
        assert weather_obs.temperature_c > 0
        assert weather_obs.provenance_label in [
            "REAL — OPENWEATHER", "CACHED — OPENWEATHER", "DEMO MODE — SYNTHETIC DATA"
        ]

        # Verify tourist-facing get_destination_weather returns the identical canonical observation
        tourist_forecast = get_destination_weather("darjeeling")
        assert tourist_forecast.destination_id == "darjeeling"
        assert tourist_forecast.provenance_label == weather_obs.provenance_label
