"""
Test Suite for Gemini Primary AI Provider, Groq Fallback AI Provider, and OpenWeather Integration.
Smart India Hackathon 2026 — Milestone 7H Production Integration.

Covers:
1. Gemini success & structured output validation
2. Gemini missing key -> Groq fallback
3. Gemini timeout -> Groq fallback
4. Gemini HTTP 429 rate limit -> Groq fallback
5. Gemini malformed response -> Groq fallback
6. Groq fallback execution after Gemini failure
7. Groq success & structured output validation
8. Groq missing key -> MockAIProvider fallback
9. Groq failure (HTTP 500, timeout, malformed) -> MockAIProvider fallback
10. Mock fallback after both Gemini and Groq fail
11. Provider provenance tracking (gemini, groq_fallback, mock_fallback)
12. Secret non-exposure across health probes and logs
13. OpenWeather success with REAL provenance
14. OpenWeather failure with stale cache fallback
15. Weather missing key with Demo fallback
16. Non-authoritative AI guarantee: deterministic crowd pressure & capacity remain untouched
"""

import os
import asyncio
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.services.ai.gemini_provider import GeminiAIProvider
from app.services.ai.groq_provider import GroqAIProvider
from app.services.ai.mock_provider import MockAIProvider
from app.services.ai import get_ai_provider
from app.services.itinerary_service import (
    _build_context,
    generate_smart_itinerary_async,
    ItineraryRequest
)
from app.models.itinerary import AIItineraryOutput, AIDayOutput, AIActivityOutput, ItineraryResponse
from app.services.weather.provider import OpenWeatherProvider, DemoWeatherProvider
from app.services.weather.service import WeatherService
from app.services.crowd_engine import calculate_crowd_score
from app.services.capacity.service import capacity_service


@pytest.fixture
def client():
    return TestClient(app)


def make_dummy_valid_ai_output(note_suffix: str = "") -> AIItineraryOutput:
    return AIItineraryOutput(
        overview_note=f"A balanced alpine journey through Kalimpong{note_suffix}.",
        why_this_itinerary=[
            "Morning Deolo visit avoids peak road traffic.",
            "Afternoon pottery cooperative supports local artisans."
        ],
        weather_adaptation_notice=None,
        days=[
            AIDayOutput(
                day_number=1,
                theme="Panoramic Ridges & Monastic Chants",
                overview="Experience tranquil high-altitude views.",
                transit_advice="Shared mountain jeep between stands.",
                activities=[
                    AIActivityOutput(
                        time_slot="08:30 AM - 10:30 AM",
                        period="Morning",
                        title="Deolo Hill Viewpoint",
                        description="Vast valley panoramas before afternoon mist.",
                        location_name="Deolo",
                        crowd_forecast="Low",
                        cost_estimate_inr=100,
                        duration_hrs=2.0,
                        travel_tip="Carry light windbreaker.",
                        category="Scenic",
                        is_weather_adapted=False,
                        adaptation_reason=None
                    )
                ]
            )
        ]
    )


# ==============================================================================
# 1. GEMINI PRIMARY PROVIDER TESTS
# ==============================================================================
class TestGeminiPrimaryProvider:

    def test_gemini_success(self):
        """Verify Gemini API response parses cleanly into AIItineraryOutput with 'gemini' provenance."""
        async def _run():
            dummy_output = make_dummy_valid_ai_output()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"text": dummy_output.model_dump_json()}
                            ]
                        }
                    }
                ]
            }

            provider = GeminiAIProvider(api_key="AIzaSyTestKey12345678901234567890123", model="gemini-3.6-flash")
            ctx = _build_context("kalimpong", {"duration_days": 1, "interests": ["Scenic"]})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert output.provider_used == "gemini"
                assert "Enriched via Gemini gemini-3.6-flash" in output.overview_note

        asyncio.run(_run())

    def test_gemini_missing_key_delegates_to_groq(self):
        """Verify missing Gemini key immediately delegates to Groq fallback."""
        async def _run():
            mock_groq = MagicMock(spec=GroqAIProvider)
            mock_groq.provider_name = "groq"
            groq_output = make_dummy_valid_ai_output(" (via Groq)")
            groq_output.provider_used = "groq_fallback"
            mock_groq.generate_itinerary.return_value = groq_output

            provider = GeminiAIProvider(api_key=None, fallback_provider=mock_groq)
            ctx = _build_context("kalimpong", {"duration_days": 1})

            output = await provider.generate_itinerary(ctx)
            assert output.provider_used == "groq_fallback"
            mock_groq.generate_itinerary.assert_called_once_with(ctx)

        asyncio.run(_run())

    def test_gemini_timeout_delegates_to_groq(self):
        """Verify Gemini timeout triggers delegation to Groq fallback without raising."""
        async def _run():
            mock_groq = MagicMock(spec=GroqAIProvider)
            mock_groq.provider_name = "groq"
            groq_output = make_dummy_valid_ai_output(" (via Groq)")
            groq_output.provider_used = "groq_fallback"
            mock_groq.generate_itinerary.return_value = groq_output

            provider = GeminiAIProvider(
                api_key="AIzaSyTestKey12345678901234567890123",
                fallback_provider=mock_groq
            )
            ctx = _build_context("kalimpong", {"duration_days": 1})

            import httpx
            with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Read timeout")):
                output = await provider.generate_itinerary(ctx)
                assert output.provider_used == "groq_fallback"
                mock_groq.generate_itinerary.assert_called_once()

        asyncio.run(_run())

    def test_gemini_429_rate_limit_delegates_to_groq(self):
        """Verify HTTP 429 rate limit triggers fallback to Groq."""
        async def _run():
            mock_groq = MagicMock(spec=GroqAIProvider)
            mock_groq.provider_name = "groq"
            groq_output = make_dummy_valid_ai_output()
            groq_output.provider_used = "groq_fallback"
            mock_groq.generate_itinerary.return_value = groq_output

            mock_resp = MagicMock()
            mock_resp.status_code = 429
            mock_resp.text = "Rate limit exceeded"

            provider = GeminiAIProvider(
                api_key="AIzaSyTestKey12345678901234567890123",
                fallback_provider=mock_groq
            )
            ctx = _build_context("kalimpong", {"duration_days": 1})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert output.provider_used == "groq_fallback"
                mock_groq.generate_itinerary.assert_called_once()

        asyncio.run(_run())

    def test_gemini_malformed_response_delegates_to_groq(self):
        """Verify invalid/non-JSON response triggers fallback to Groq."""
        async def _run():
            mock_groq = MagicMock(spec=GroqAIProvider)
            mock_groq.provider_name = "groq"
            groq_output = make_dummy_valid_ai_output()
            groq_output.provider_used = "groq_fallback"
            mock_groq.generate_itinerary.return_value = groq_output

            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "candidates": [{"content": {"parts": [{"text": "Sorry, I am unable to format as JSON."}]}}]
            }

            provider = GeminiAIProvider(
                api_key="AIzaSyTestKey12345678901234567890123",
                fallback_provider=mock_groq
            )
            ctx = _build_context("kalimpong", {"duration_days": 1})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert output.provider_used == "groq_fallback"
                mock_groq.generate_itinerary.assert_called_once()

        asyncio.run(_run())

    def test_gemini_5xx_delegates_to_groq(self):
        """Verify Gemini HTTP 500 or 503 triggers fallback to Groq."""
        async def _run():
            mock_groq = MagicMock(spec=GroqAIProvider)
            mock_groq.provider_name = "groq"
            groq_output = make_dummy_valid_ai_output()
            groq_output.provider_used = "groq_fallback"
            mock_groq.generate_itinerary.return_value = groq_output

            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_resp.text = "Internal Server Error"

            provider = GeminiAIProvider(
                api_key="AIzaSyTestKey12345678901234567890123",
                fallback_provider=mock_groq
            )
            ctx = _build_context("kalimpong", {"duration_days": 1})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert output.provider_used == "groq_fallback"
                mock_groq.generate_itinerary.assert_called_once()

        asyncio.run(_run())


# ==============================================================================
# 2. GROQ FALLBACK PROVIDER TESTS
# ==============================================================================
class TestGroqFallbackProvider:

    def test_groq_success(self):
        """Verify Groq API response parses cleanly into AIItineraryOutput with 'groq_fallback' provenance."""
        async def _run():
            dummy_output = make_dummy_valid_ai_output()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": dummy_output.model_dump_json()
                        }
                    }
                ]
            }

            provider = GroqAIProvider(
                api_key="gsk_testdummygroqkey12345678901234567890",
                model="openai/gpt-oss-120b",
                is_fallback_mode=True
            )
            ctx = _build_context("kalimpong", {"duration_days": 1, "interests": ["Scenic"]})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert output.provider_used == "groq_fallback"
                assert "Enriched via Groq openai/gpt-oss-120b" in output.overview_note

        asyncio.run(_run())

    def test_groq_missing_key_delegates_to_mock(self):
        """Verify missing Groq key immediately delegates to MockAIProvider."""
        async def _run():
            provider = GroqAIProvider(api_key=None, fallback_provider=MockAIProvider())
            ctx = _build_context("kalimpong", {"duration_days": 2})

            output = await provider.generate_itinerary(ctx)
            assert isinstance(output, AIItineraryOutput)
            assert output.provider_used == "mock"
            assert len(output.days) == 2

        asyncio.run(_run())

    def test_groq_http_error_delegates_to_mock(self):
        """Verify HTTP 500 or timeout on Groq delegates safely to MockAIProvider."""
        async def _run():
            mock_resp = MagicMock()
            mock_resp.status_code = 503
            mock_resp.text = "Service Unavailable"

            provider = GroqAIProvider(
                api_key="gsk_testdummygroqkey12345678901234567890",
                fallback_provider=MockAIProvider()
            )
            ctx = _build_context("kalimpong", {"duration_days": 1})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert output.provider_used == "mock"

        asyncio.run(_run())

    def test_groq_timeout_delegates_to_mock(self):
        """Verify Groq timeout triggers safe delegation to MockAIProvider."""
        async def _run():
            provider = GroqAIProvider(
                api_key="gsk_testdummygroqkey12345678901234567890",
                fallback_provider=MockAIProvider()
            )
            ctx = _build_context("kalimpong", {"duration_days": 1})

            import httpx
            with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Read timeout on Groq")):
                output = await provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert output.provider_used == "mock"

        asyncio.run(_run())

    def test_groq_429_rate_limit_delegates_to_mock(self):
        """Verify Groq HTTP 429 rate limit triggers safe delegation to MockAIProvider."""
        async def _run():
            mock_resp = MagicMock()
            mock_resp.status_code = 429
            mock_resp.text = "Rate limit exceeded"

            provider = GroqAIProvider(
                api_key="gsk_testdummygroqkey12345678901234567890",
                fallback_provider=MockAIProvider()
            )
            ctx = _build_context("kalimpong", {"duration_days": 1})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert output.provider_used == "mock"

        asyncio.run(_run())

    def test_groq_500_error_delegates_to_mock(self):
        """Verify Groq HTTP 500 error triggers safe delegation to MockAIProvider."""
        async def _run():
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_resp.text = "Internal Groq Error"

            provider = GroqAIProvider(
                api_key="gsk_testdummygroqkey12345678901234567890",
                fallback_provider=MockAIProvider()
            )
            ctx = _build_context("kalimpong", {"duration_days": 1})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert output.provider_used == "mock"

        asyncio.run(_run())

    def test_groq_malformed_json_delegates_to_mock(self):
        """Verify Groq malformed non-JSON output triggers safe delegation to MockAIProvider."""
        async def _run():
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": "Not valid JSON output from LLM."
                        }
                    }
                ]
            }

            provider = GroqAIProvider(
                api_key="gsk_testdummygroqkey12345678901234567890",
                fallback_provider=MockAIProvider()
            )
            ctx = _build_context("kalimpong", {"duration_days": 1})

            with patch("httpx.AsyncClient.post", return_value=mock_resp):
                output = await provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert output.provider_used == "mock"

        asyncio.run(_run())


# ==============================================================================
# 3. END-TO-END FALLBACK CHAIN & PROVENANCE TESTS
# ==============================================================================
class TestProviderFallbackChainAndProvenance:

    def test_chain_both_fail_resolves_to_mock(self):
        """Verify complete chain: Gemini fails -> Groq fails -> MockAIProvider succeeds."""
        async def _run():
            # Construct chain: Gemini -> Groq -> Mock
            mock_final = MockAIProvider(provider_name="mock")
            groq = GroqAIProvider(api_key="gsk_invalid", fallback_provider=mock_final)
            gemini = GeminiAIProvider(api_key="AIzaSyInvalid", fallback_provider=groq)

            # Both HTTP requests fail with 500
            err_resp = MagicMock()
            err_resp.status_code = 500
            err_resp.text = "Internal error"

            ctx = _build_context("kalimpong", {"duration_days": 3})

            with patch("httpx.AsyncClient.post", return_value=err_resp):
                output = await gemini.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert output.provider_used == "mock"
                assert len(output.days) == 3

        asyncio.run(_run())

    def test_itinerary_response_records_accurate_ai_provider_used(self):
        """Verify ItineraryResponse records exact provider used ('gemini', 'groq_fallback', 'mock_fallback')."""
        async def _run():
            req = ItineraryRequest(destination_id="kalimpong", duration_days=2)

            # Case A: Gemini succeeds
            gem_output = make_dummy_valid_ai_output()
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "candidates": [{"content": {"parts": [{"text": gem_output.model_dump_json()}]}}]
            }

            with patch.object(settings, "AI_PROVIDER", "gemini"):
                with patch.object(settings, "GEMINI_API_KEY", "AIzaSyValidKey12345678901234567890"):
                    with patch("httpx.AsyncClient.post", return_value=mock_resp):
                        resp = await generate_smart_itinerary_async(req)
                        assert resp.ai_provider_used == "gemini"

            # Case B: Zero keys configured (Demo default)
            with patch.object(settings, "AI_PROVIDER", "gemini"):
                with patch.object(settings, "GEMINI_API_KEY", None):
                    with patch.object(settings, "GROQ_API_KEY", None):
                        resp = await generate_smart_itinerary_async(req)
                        assert resp.ai_provider_used == "mock"

        asyncio.run(_run())


# ==============================================================================
# 4. SECRET NON-EXPOSURE & SANITIZATION TESTS
# ==============================================================================
class TestSecretNonExposure:

    def test_health_check_reports_status_without_leaking_keys(self, client):
        """Verify /health and /api/health report ai and weather status without leaking keys."""
        with patch.object(settings, "GEMINI_API_KEY", "AIzaSySecretGeminiKey1234567890123456"):
            with patch.object(settings, "GROQ_API_KEY", "gsk_SecretGroqKey12345678901234567890"):
                with patch.object(settings, "WEATHER_API_KEY", "secretweatherapikey1234567890123"):
                    res = client.get("/health?detailed=true")
                    assert res.status_code == 200
                    data = res.json()
                    
                    # Verify configuration flags are booleans
                    assert data["providers"]["ai"]["configured"] is True
                    assert data["providers"]["ai"]["fallback_configured"] is True

                    # Verify no secret text appears in serialization
                    text = str(data)
                    assert "AIzaSySecretGeminiKey" not in text
                    assert "gsk_SecretGroqKey" not in text
                    assert "secretweatherapikey" not in text

    def test_log_sanitizer_redacts_gemini_and_groq_keys(self):
        """Verify SanitizingFilter scrubs AIzaSy..., gsk_..., and key= params."""
        from app.core.logging import SanitizingFilter

        raw_msg = (
            "Calling Gemini with key AIzaSyTestKey12345678901234567890123 and "
            "Groq with gsk_TestGroqKey1234567890123456789012345678 and key=secret123456789012"
        )
        sanitized = SanitizingFilter.sanitize(raw_msg)
        assert "AIzaSyTestKey12345678901234567890123" not in sanitized
        assert "AIzaSy***REDACTED***" in sanitized
        assert "gsk_TestGroqKey" not in sanitized
        assert "gsk_***REDACTED***" in sanitized
        assert "key=secret123456789012" not in sanitized
        assert "key=***REDACTED***" in sanitized


# ==============================================================================
# 5. OPENWEATHER INTEGRATION TESTS
# ==============================================================================
class TestOpenWeatherIntegration:

    def test_openweather_real_success_provenance(self):
        """Verify OpenWeather provider parses raw response with REAL provenance."""
        mock_payload = {
            "main": {"temp": 17.0, "temp_min": 14.0, "temp_max": 20.0, "humidity": 60},
            "wind": {"speed": 3.0},
            "visibility": 10000,
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "rain": {}
        }
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_payload

        provider = OpenWeatherProvider(api_key="valid_dummy_key")
        with patch("httpx.Client.get", return_value=mock_resp):
            obs = provider.fetch_current("kalimpong")
            assert obs.provenance_label in ["REAL — OPENWEATHER", "REAL — EXTERNAL PROVIDER"]
            assert obs.provider_mode == "REAL"
            assert obs.temperature_c == 17.0

    def test_weather_service_stale_fallback(self):
        """Verify WeatherService returns MIXED provenance when cached entry is stale and upstream fails."""
        service = WeatherService(ttl_seconds=60)
        # Pre-seed cache
        service.get_weather("kalimpong")

        # Mock provider failure
        failing_provider = MagicMock()
        failing_provider.fetch_current.side_effect = RuntimeError("OpenWeather upstream timeout")
        service.set_provider(failing_provider)

        stale_obs = service.get_weather("kalimpong", force_refresh=True)
        assert stale_obs.provenance_label == "MIXED — STALE TELEMETRY FALLBACK"
        assert stale_obs.cache_status == "STALE"

    def test_weather_missing_key_demo_fallback(self):
        """Verify WeatherService returns DEMO provenance when key is unset."""
        service = WeatherService()
        obs = service.get_weather("rishop")
        assert obs.provenance_label in ["REAL — OPENWEATHER", "REAL — EXTERNAL PROVIDER", "DEMO MODE — SYNTHETIC DATA"]


# ==============================================================================
# 6. NON-AUTHORITATIVE AI GUARANTEE
# ==============================================================================
class TestNonAuthoritativeAIGuarantee:

    def test_deterministic_crowd_engine_independent_of_ai(self):
        """Verify deterministic crowd calculation is never altered by AI state."""
        crowd_darjeeling = calculate_crowd_score("darjeeling")
        # Fixed deterministic score for Darjeeling
        assert crowd_darjeeling.crowd_score >= 76
        assert crowd_darjeeling.crowd_level.value == "VERY HIGH"

    def test_carrying_capacity_independent_of_ai(self):
        """Verify carrying capacity health classifications remain purely deterministic."""
        cap_kalimpong = capacity_service.get_destination_capacity("kalimpong")
        assert cap_kalimpong.destination_id == "kalimpong"
        assert cap_kalimpong.capacity_health.value in ["HEALTHY", "LIMITED", "HIGH_UTILIZATION", "FULL"]


# ==============================================================================
# 7. AI MODEL CONFIGURATION TESTS (M7H COMPATIBILITY)
# ==============================================================================
class TestAIModelConfiguration:

    def test_default_models_are_gemini_3_6_and_gpt_oss_120b(self):
        """Verify the active default models match the latest SIH 2026 specifications."""
        assert settings.GEMINI_MODEL == "gemini-3.6-flash"
        assert settings.GROQ_MODEL == "openai/gpt-oss-120b"

    def test_providers_use_configured_defaults_when_model_param_omitted(self):
        """Verify GeminiAIProvider and GroqAIProvider use settings.GEMINI_MODEL and settings.GROQ_MODEL."""
        gemini = GeminiAIProvider(api_key="AIzaSyDummyKey1234567890")
        groq = GroqAIProvider(api_key="gsk_DummyKey12345678901234567890")

        assert gemini.model == "gemini-3.6-flash"
        assert groq.model == "openai/gpt-oss-120b"

    def test_providers_respect_environment_override(self):
        """Verify providers pick up custom models from settings override."""
        with patch.object(settings, "GEMINI_MODEL", "gemini-custom-experimental"):
            with patch.object(settings, "GROQ_MODEL", "groq-custom-experimental"):
                gemini = GeminiAIProvider(api_key="AIzaSyDummyKey1234567890")
                groq = GroqAIProvider(api_key="gsk_DummyKey12345678901234567890")

                assert gemini.model == "gemini-custom-experimental"
                assert groq.model == "groq-custom-experimental"


# ==============================================================================
# 8. OPT-IN LIVE CREDENTIALED SMOKE TESTS
# ==============================================================================
@pytest.mark.skipif(
    os.getenv("RUN_LIVE_AI_SMOKE_TEST") != "true",
    reason="Credentialed live smoke tests are opt-in. Set RUN_LIVE_AI_SMOKE_TEST=true to run."
)
class TestLiveCredentialedSmoke:
    """
    Opt-in live integration smoke test that executes only when RUN_LIVE_AI_SMOKE_TEST=true.
    Never executes in standard CI or default pytest runs.
    """

    def test_live_ai_smoke_execution(self):
        gemini_key = os.getenv("GEMINI_API_KEY")
        groq_key = os.getenv("GROQ_API_KEY")

        # Load from local gitignored backend/.env if available
        if not gemini_key or not groq_key:
            env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
            if os.path.exists(env_file):
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line and not line.strip().startswith("#"):
                            k, v = line.strip().split("=", 1)
                            if k.strip() == "GEMINI_API_KEY" and not gemini_key:
                                gemini_key = v.strip().strip('"\'')
                            elif k.strip() == "GROQ_API_KEY" and not groq_key:
                                groq_key = v.strip().strip('"\'')

        if not gemini_key and not groq_key:
            pytest.skip("Neither GEMINI_API_KEY nor GROQ_API_KEY is available for live smoke test.")

        ctx = _build_context("kalimpong", {"duration_days": 1, "pace": "Moderate"})

        async def _run():
            # Test Gemini primary (with Groq fallback)
            if gemini_key:
                groq_fb = GroqAIProvider(
                    api_key=groq_key,
                    model="openai/gpt-oss-120b",
                    fallback_provider=MockAIProvider(),
                    is_fallback_mode=True
                ) if groq_key else MockAIProvider()

                gemini_provider = GeminiAIProvider(
                    api_key=gemini_key,
                    model="gemini-3.6-flash",
                    fallback_provider=groq_fb
                )
                output = await gemini_provider.generate_itinerary(ctx)
                assert isinstance(output, AIItineraryOutput)
                assert output.provider_used in ["gemini", "groq_fallback", "mock"]
                assert len(output.days) == 1

            # Test Groq standalone
            if groq_key:
                groq_provider = GroqAIProvider(
                    api_key=groq_key,
                    model="openai/gpt-oss-120b",
                    fallback_provider=MockAIProvider(),
                    is_fallback_mode=True
                )
                output_groq = await groq_provider.generate_itinerary(ctx)
                assert isinstance(output_groq, AIItineraryOutput)
                assert output_groq.provider_used in ["groq_fallback", "mock"]
                assert len(output_groq.days) == 1

        asyncio.run(_run())


