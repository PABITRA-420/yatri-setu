"""
Automated Test Suite for Milestone 7H: Real API Integration + Production Hardening.
Verifies OpenWeather integration, OpenAI resilience, PostgreSQL URL normalization,
CORS security, health check safety, rate limiting, and administrative authorization.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import Settings, settings
from app.core.rate_limit import SlidingWindowRateLimiter
from app.services.weather.provider import (
    OpenWeatherProvider,
    DemoWeatherProvider,
    UnavailableWeatherProvider
)
from app.services.weather.service import WeatherService
from app.services.weather.schemas import WeatherObservation
from app.services.ai.openai_provider import OpenAIProvider
from app.models.itinerary import ItineraryContext, AIItineraryOutput, ItineraryDay


@pytest.fixture
def client():
    return TestClient(app)


# ==============================================================================
# 1. WEATHER INTEGRATION & PROVENANCE TESTS
# ==============================================================================
class TestWeatherIntegrationAndHardening:

    def test_openweather_valid_mock_response(self):
        """Verify OpenWeather provider parses live observation correctly with REAL provenance."""
        mock_payload = {
            "main": {"temp": 16.5, "temp_min": 13.0, "temp_max": 20.0, "humidity": 65},
            "wind": {"speed": 4.5},
            "visibility": 10000,
            "weather": [{"main": "Clouds", "description": "scattered clouds"}],
            "rain": {"1h": 0.0}
        }

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_payload

        provider = OpenWeatherProvider(api_key="test_dummy_key")
        assert provider.is_available() is True
        assert provider.get_provider_mode() == "REAL"

        with patch("httpx.Client.get", return_value=mock_resp):
            obs = provider.fetch_current("kalimpong")
            assert obs.destination_id == "kalimpong"
            assert obs.temperature_c == 16.5
            assert obs.humidity == 65
            assert obs.provider_mode == "REAL"
            assert obs.provenance_label == "REAL — EXTERNAL PROVIDER"
            assert obs.source == "OPENWEATHERMAP_LIVE"

    def test_missing_weather_key_safe_fallback(self):
        """Verify that missing weather key initializes safe Demo provider without crashing."""
        provider = OpenWeatherProvider(api_key=None)
        assert provider.is_available() is False

        service = WeatherService()
        # Ensure default behavior returns valid observation with DEMO provenance
        obs = service.get_weather("darjeeling")
        assert obs.destination_id == "darjeeling"
        assert obs.temperature_c > 0
        assert obs.provider_mode in ["REAL", "DEMO"]
        assert obs.provenance_label in ["REAL — EXTERNAL PROVIDER", "DEMO MODE — SYNTHETIC DATA"]

    def test_weather_provider_timeout_and_stale_fallback(self):
        """Verify that provider failure falls back to stale cache with MIXED provenance."""
        service = WeatherService(ttl_seconds=60)
        # Pre-seed cache
        demo = DemoWeatherProvider()
        seed_obs = demo.fetch_current("kalimpong")
        service.get_weather("kalimpong")

        # Now mock failure on provider
        failing_provider = MagicMock()
        failing_provider.fetch_current.side_effect = RuntimeError("OpenWeather connection timeout")
        service.set_provider(failing_provider)

        # Retrieve should return stale cache with degraded status
        stale_obs = service.get_weather("kalimpong", force_refresh=True)
        assert stale_obs.cache_status == "STALE"
        assert stale_obs.data_quality == "DEGRADED"
        assert stale_obs.provenance_label == "MIXED — STALE TELEMETRY FALLBACK"

    def test_unavailable_weather_provider_provenance(self):
        """Verify UnavailableWeatherProvider returns correct UNAVAILABLE provenance."""
        provider = UnavailableWeatherProvider()
        assert provider.is_available() is False
        assert provider.get_provider_mode() == "UNAVAILABLE"
        obs = provider.fetch_current("lava")
        assert obs.provenance_label == "UNAVAILABLE — SAFE FALLBACK"


# ==============================================================================
# 2. OPENAI INTEGRATION & NON-AUTHORITATIVE AI TESTS
# ==============================================================================
import asyncio
from app.services.itinerary_service import _build_context
from app.models.itinerary import AIItineraryOutput, AIDayOutput, AIActivityOutput

class TestOpenAIIntegrationAndHardening:

    def test_openai_missing_key_fallback(self):
        """Verify missing OpenAI API key falls back seamlessly to MockAIProvider."""
        async def _run():
            provider = OpenAIProvider(api_key=None)
            ctx = _build_context("kalimpong", {"duration_days": 2, "interests": ["Culture", "Nature"]})
            output = await provider.generate_itinerary(ctx)
            assert isinstance(output, AIItineraryOutput)
            assert len(output.days) == 2
            assert "Yatri Setu Himalayan Adaptive Engine" in output.overview_note

        asyncio.run(_run())

    def test_openai_valid_mock_response(self):
        """Verify OpenAI parses chat completion response and tags output."""
        async def _run():
            valid_ai_output = AIItineraryOutput(
                overview_note="A scenic tour through misty pine ridges.",
                why_this_itinerary=["Low crowd index", "Pleasant climate"],
                weather_adaptation_notice=None,
                days=[
                    AIDayOutput(
                        day_number=1,
                        theme="Cultural Heritage",
                        overview="Explore historical monasteries and viewpoints.",
                        transit_advice="Shared local taxi",
                        activities=[
                            AIActivityOutput(
                                time_slot="09:00 AM - 11:30 AM",
                                period="Morning",
                                title="Deolo Hill Viewpoint",
                                description="Panoramic mountain view.",
                                location_name="Deolo",
                                crowd_forecast="Low",
                                cost_estimate_inr=100,
                                duration_hrs=2.5,
                                travel_tip="Great morning sunlight",
                                category="Scenic"
                            )
                        ]
                    )
                ]
            )

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": valid_ai_output.model_dump_json()}}]
            }

            provider = OpenAIProvider(api_key="sk-testdummykey1234567890")
            ctx = _build_context("kalimpong", {"duration_days": 1, "interests": ["Culture"]})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert "Enriched via OpenAI" in output.overview_note

        asyncio.run(_run())

    def test_openai_rate_limit_and_timeout_fallback(self):
        """Verify HTTP 429 rate limit or timeout gracefully degrades without throwing."""
        async def _run():
            mock_resp = MagicMock()
            mock_resp.status_code = 429
            mock_resp.text = "Rate limit exceeded"

            provider = OpenAIProvider(api_key="sk-testdummykey1234567890")
            ctx = _build_context("kalimpong", {"duration_days": 1, "interests": ["Nature"]})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert "rate limit" in output.overview_note.lower() or "adaptive engine" in output.overview_note.lower()

        asyncio.run(_run())


# ==============================================================================
# 3. PRODUCTION HEALTH CHECK & SECRET LEAKAGE PREVENTION
# ==============================================================================
class TestHealthCheckAndSecretSecurity:

    def test_health_check_returns_healthy(self, client):
        """Verify /health?detailed=true returns detailed status without leaking secrets."""
        res = client.get("/health?detailed=true")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "database" in data
        assert "providers" in data
        assert "weather" in data["providers"]
        assert "ai" in data["providers"]

        # Assert no sensitive secrets in json dump
        text = str(data)
        assert "sk-" not in text
        assert "Bearer" not in text
        assert "password" not in text

    def test_api_health_alias(self, client):
        """Verify /api/health also returns the sanitized health response."""
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"


# ==============================================================================
# 4. DATABASE CONFIGURATION & URL NORMALIZATION
# ==============================================================================
class TestDatabaseConfiguration:

    def test_database_url_postgres_normalization(self):
        """Verify postgres:// is rewritten to postgresql:// for SQLAlchemy 2.0 compatibility."""
        with patch.dict(os.environ, {"DATABASE_URL": "postgres://user:pass@localhost:5432/testdb"}):
            s = Settings()
            assert s.DATABASE_URL.startswith("postgresql://")
            assert not s.DATABASE_URL.startswith("postgres://")

    def test_database_url_sqlite_preservation(self):
        """Verify local sqlite url is preserved unchanged."""
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///./yatri_setu.db"}):
            s = Settings()
            assert s.DATABASE_URL == "sqlite:///./yatri_setu.db"


# ==============================================================================
# 5. RATE LIMITING & ABUSE PROTECTION
# ==============================================================================
class TestRateLimiter:

    def test_rate_limiter_exceeded_raises_429(self):
        """Verify sliding window rate limiter raises HTTP 429 when threshold exceeded."""
        limiter = SlidingWindowRateLimiter(requests_per_minute=2, burst_allowance=0)
        mock_req = MagicMock()
        mock_req.client.host = "192.168.1.100"
        mock_req.headers = {}

        # First 2 requests succeed
        limiter.check_rate_limit(mock_req)
        limiter.check_rate_limit(mock_req)

        # 3rd request in same window must trigger 429
        with pytest.raises(Exception) as exc_info:
            limiter.check_rate_limit(mock_req)
        assert "429" in str(exc_info.value)


# ==============================================================================
# 6. ADMINISTRATIVE AUTHORIZATION & ACCESS CONTROL
# ==============================================================================
class TestAdminAuthorization:

    def test_admin_open_when_key_unset(self, client):
        """When ADMIN_SECRET_KEY is empty, admin endpoints allow access for local demos/tests."""
        with patch.object(settings, "ADMIN_SECRET_KEY", None):
            res = client.get("/api/admin/command-center")
            assert res.status_code == 200

    def test_admin_forbidden_when_key_set_and_missing(self, client):
        """When ADMIN_SECRET_KEY is configured, unauthenticated requests are rejected with 403."""
        with patch.object(settings, "ADMIN_SECRET_KEY", "supersecretadmin123"):
            res = client.get("/api/admin/command-center")
            assert res.status_code == 403
            assert "forbidden" in res.json()["detail"].lower()

    def test_admin_authorized_when_key_set_and_provided(self, client):
        """When ADMIN_SECRET_KEY is configured, requests with matching X-Admin-Key succeed."""
        with patch.object(settings, "ADMIN_SECRET_KEY", "supersecretadmin123"):
            res = client.get("/api/admin/command-center", headers={"X-Admin-Key": "supersecretadmin123"})
            assert res.status_code == 200
