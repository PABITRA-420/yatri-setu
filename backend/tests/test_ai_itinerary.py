"""
Tests for Milestone 2B: Adaptive AI Travel Intelligence (Smart India Hackathon 2026)
Tests AI provider abstraction, mock provider adaptation, weather-aware scheduling,
sustainability metrics, and optimization directives.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.itinerary import (
    ItineraryRequest,
    ItineraryOptimizeRequest,
    ItineraryContext
)
from app.services.ai import get_ai_provider, MockAIProvider, ClaudeAIProvider, OpenAIProvider
from app.services.weather_service import get_destination_weather
from app.services.route_service import get_route_estimate
from app.services.sustainability_engine import calculate_sustainability
from app.services.itinerary_service import (
    generate_smart_itinerary,
    optimize_smart_itinerary
)

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_deterministic_weather_for_itinerary():
    from app.services import weather_service
    original = weather_service.weather_provider
    weather_service.weather_provider = weather_service.MockWeatherProvider()
    yield
    weather_service.weather_provider = original


def test_weather_service():
    """Verify deterministic weather profiles and rain flags for mountain destinations."""
    darj_weather = get_destination_weather("darjeeling")
    assert darj_weather.destination_id == "darjeeling"
    assert darj_weather.mountain_visibility_score >= 80
    assert darj_weather.rain_expected is False

    lava_weather = get_destination_weather("lava")
    assert lava_weather.destination_id == "lava"
    assert lava_weather.rain_expected is True
    assert lava_weather.precipitation_chance_percent >= 50
    assert "drizzle" in lava_weather.condition.lower() or "mist" in lava_weather.condition.lower()

def test_route_service():
    """Verify route estimation between Himalayan circuit destinations."""
    route = get_route_estimate("darjeeling", "kalimpong")
    assert route.distance_km == 50.0
    assert route.duration_minutes > 90
    assert "Peshok" in route.transit_mode or "Shared" in route.transit_mode
    assert route.carbon_emissions_kg > 0

    local_route = get_route_estimate("kalimpong", "kalimpong")
    assert local_route.distance_km < 10.0
    assert local_route.shared_transit_available is True

def test_sustainability_engine():
    """Verify deterministic 0-100 sustainability scorecard and local retention impact."""
    scorecard = calculate_sustainability(
        destination_id="lava",
        total_budget_inr=9000,
        crowd_score=25,
        num_days=3,
        prefers_shared_transit=True,
        homestay_selected=True
    )
    assert 0 <= scorecard.sustainability_score <= 100
    assert scorecard.sustainability_classification in ["EXCELLENT", "HIGH"]
    assert len(scorecard.factors) == 5
    assert scorecard.tourism_impact.direct_village_economy_percent >= 80
    assert scorecard.tourism_impact.community_fund_contribution_inr > 0
    assert scorecard.tourism_impact.carbon_saved_vs_private_car_kg > 0

def test_ai_provider_factory_and_fallback():
    """Verify default provider is mock and invalid inputs gracefully fall back to mock."""
    prov_mock = get_ai_provider("mock")
    assert isinstance(prov_mock, MockAIProvider)
    assert prov_mock.provider_name == "mock"

    prov_invalid = get_ai_provider("unknown_provider")
    assert isinstance(prov_invalid, MockAIProvider)

    # Claude and OpenAI provider instances
    prov_claude = get_ai_provider("claude")
    assert isinstance(prov_claude, ClaudeAIProvider)
    assert prov_claude.provider_name == "claude"

    prov_openai = get_ai_provider("openai")
    assert isinstance(prov_openai, OpenAIProvider)
    assert prov_openai.provider_name == "openai"

def test_weather_aware_adaptation_in_lava():
    """Verify that when rain is expected (Lava), afternoon activities are flagged and adapted."""
    req = ItineraryRequest(
        destination_id="lava",
        duration_days=2,
        traveler_type="Solo",
        pace="Moderate",
        interests=["Nature", "Culture"]
    )
    resp = generate_smart_itinerary(req)
    assert resp.destination_id == "lava"
    assert resp.duration_days == 2
    assert resp.weather_forecast is not None
    assert resp.weather_forecast.rain_expected is True
    assert any(w in resp.weather_adaptation_notice.lower() for w in ["adapted", "shifted", "drizzle", "rain", "covered", "rescheduled"])

    # Check that at least one afternoon activity is flagged
    weather_adapted_found = False
    for day in resp.days:
        for act in day.activities:
            if act.is_weather_adapted:
                weather_adapted_found = True
                assert "Yatri Setu adapted" in act.adaptation_reason
                assert any(p in act.period for p in ["Morning", "Afternoon", "Evening"])

    assert weather_adapted_found is True

def test_itinerary_sustainability_fields():
    """Verify that generated itineraries have SIH sustainability scorecard fields populated."""
    req = ItineraryRequest(
        destination_id="kalimpong",
        duration_days=3,
        traveler_type="Couple",
        pace="Moderate"
    )
    resp = generate_smart_itinerary(req)
    assert resp.sustainability_score >= 70
    assert resp.sustainability_classification in ["EXCELLENT", "HIGH"]
    assert resp.tourism_impact is not None
    assert resp.tourism_impact.estimated_local_spend_inr > 0
    assert resp.ai_provider_used in ["mock", "groq_fallback", "gemini"]

def test_itinerary_optimization_directives():
    """Verify optimization directives modify itineraries deterministically."""
    base_req = ItineraryRequest(
        destination_id="darjeeling",
        duration_days=2,
        traveler_type="Solo",
        pace="Moderate"
    )
    base_resp = generate_smart_itinerary(base_req)

    # 1. MAKE_CHEAPER
    cheaper_req = ItineraryOptimizeRequest(
        itinerary_id=base_resp.itinerary_id,
        destination_id="darjeeling",
        instruction="MAKE_CHEAPER",
        current_itinerary=base_resp
    )
    cheaper_resp = optimize_smart_itinerary(cheaper_req)
    assert cheaper_resp.total_estimated_budget_inr < base_resp.total_estimated_budget_inr
    assert any("budget" in w.lower() for w in cheaper_resp.why_this_itinerary)
    assert "MAKE_CHEAPER" in cheaper_resp.optimization_history[0]

    # 2. MORE_RELAXED
    relaxed_req = ItineraryOptimizeRequest(
        itinerary_id=base_resp.itinerary_id,
        destination_id="darjeeling",
        instruction="MORE_RELAXED",
        current_itinerary=base_resp
    )
    relaxed_resp = optimize_smart_itinerary(relaxed_req)
    for day in relaxed_resp.days:
        assert len(day.activities) <= 2

    # 3. RAIN_SAFE
    rain_req = ItineraryOptimizeRequest(
        itinerary_id=base_resp.itinerary_id,
        destination_id="darjeeling",
        instruction="RAIN_SAFE",
        current_itinerary=base_resp
    )
    rain_resp = optimize_smart_itinerary(rain_req)
    assert rain_resp.weather_adaptation_notice is not None
    rain_adapted = any(act.is_weather_adapted for d in rain_resp.days for act in d.activities)
    assert rain_adapted is True

def test_api_generate_and_optimize_endpoints():
    """Verify API endpoints POST /api/itinerary/generate and POST /api/itinerary/optimize."""
    # 1. Generate
    gen_payload = {
        "destination_id": "rishop",
        "duration_days": 2,
        "traveler_type": "Solo",
        "pace": "Moderate",
        "interests": ["Nature", "Scenic"]
    }
    gen_res = client.post("/api/itinerary/generate", json=gen_payload)
    assert gen_res.status_code == 200
    itin = gen_res.json()
    assert itin["destination_id"] == "rishop"
    assert len(itin["days"]) == 2
    assert "sustainability_score" in itin
    assert itin["ai_provider_used"] in ["mock", "groq_fallback", "gemini"]

    # 2. Optimize
    opt_payload = {
        "itinerary_id": itin["itinerary_id"],
        "destination_id": "rishop",
        "instruction": "MORE_NATURE",
        "current_itinerary": itin
    }
    opt_res = client.post("/api/itinerary/optimize", json=opt_payload)
    assert opt_res.status_code == 200
    opt_data = opt_res.json()
    assert len(opt_data["optimization_history"]) == 1
    assert "MORE_NATURE" in opt_data["optimization_history"][0]
    assert any("Nature" in d["theme"] or "Forest" in d["theme"] for d in opt_data["days"])

def test_api_weather_endpoint():
    """Verify GET /api/destinations/{id}/weather endpoint."""
    res = client.get("/api/destinations/kalimpong/weather")
    assert res.status_code == 200
    w_data = res.json()
    assert w_data["destination_id"] == "kalimpong"
    assert w_data["destination_name"] == "Kalimpong"
    assert "temperature_range_c" in w_data
    assert "mountain_visibility_score" in w_data

    # 404 for unknown
    res_404 = client.get("/api/destinations/nonexistent_place/weather")
    assert res_404.status_code == 404
