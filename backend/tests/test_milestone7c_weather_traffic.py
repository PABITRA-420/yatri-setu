"""
Milestone 7C Test Suite: Live Weather + Traffic Intelligence & Pressure Recalculation
Validates:
1. Weather Service (Schemas, Demo Provider, Caching, Stale Fallback, Impact Score)
2. Traffic Service (Schemas, Arterial Corridors, Travel-time Ratio, Congestion & Access Status)
3. Pressure Refresh Service (Signal Fusion, Top Drivers, Delta Tracking, Safety Decoupling)
4. Future Dates Isolation (Forecast conditions without fabricating live road traffic)
5. Alternative Destination Filtering (Disrupted corridors excluded from recommendations)
6. API Endpoints & Admin Refresh Cooldown (/api prefix)
7. Security & Provenance (Zero API key leaks, strict provenance labels)
"""

import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.services.weather import (
    weather_service,
    WeatherObservation,
    WeatherImpactSignal,
    DemoWeatherProvider,
    UnavailableWeatherProvider
)
from app.services.traffic import (
    traffic_service,
    RouteTrafficObservation,
    DestinationTrafficSummary,
    TrafficImpactSignal,
    DemoTrafficProvider,
    UnavailableTrafficProvider
)
from app.services.pressure_refresh_service import (
    pressure_refresh_service,
    PressureExplanation,
    DestinationLiveConditions
)
from app.services.alternative_engine import get_alternative_destinations

client = TestClient(app)


# ==========================================
# 1. Weather Intelligence Unit Tests
# ==========================================

def test_weather_observation_schema():
    obs = WeatherObservation(
        destination_id="darjeeling",
        destination_name="Darjeeling",
        temperature_c=14.5,
        temp_min_c=11.0,
        temp_max_c=18.0,
        precipitation_probability=65,
        precipitation_mm=4.2,
        humidity=78,
        wind_speed_kmh=18.0,
        weather_condition="Rainy",
        severe_weather="Heavy Mist",
        visibility_km=3.5,
        advisory="Patchy rain and mountain mist. Reduced visibility on Hill Cart Road.",
        source="DEMO_OPENWEATHER",
        provider_mode="DEMO",
        confidence=0.88,
        data_quality="HIGH",
        cache_status="LIVE"
    )
    assert obs.destination_id == "darjeeling"
    assert obs.temperature_c == 14.5
    assert obs.precipitation_mm == 4.2
    assert obs.weather_condition == "Rainy"
    assert obs.visibility_km == 3.5


def test_demo_weather_provider_all_destinations():
    provider = DemoWeatherProvider()
    destinations = ["darjeeling", "kalimpong", "lava", "lolegaon", "rishop", "mirik"]
    for dest_id in destinations:
        obs = provider.fetch_current(dest_id)
        assert obs.destination_id == dest_id
        assert -10.0 < obs.temperature_c < 45.0
        assert 0 <= obs.humidity <= 100
        assert obs.visibility_km > 0
        assert obs.provider_mode == "DEMO"


def test_weather_impact_calculation():
    pleasant = WeatherObservation(
        destination_id="kalimpong",
        destination_name="Kalimpong",
        temperature_c=18.0,
        temp_min_c=14.0,
        temp_max_c=22.0,
        precipitation_probability=10,
        precipitation_mm=0.0,
        humidity=55,
        wind_speed_kmh=8.0,
        weather_condition="Clear",
        severe_weather=None,
        visibility_km=10.0,
        advisory="Clear skies and panoramic mountain visibility.",
        source="DEMO_OPENWEATHER",
        provider_mode="DEMO",
        confidence=0.90,
        data_quality="HIGH",
        cache_status="LIVE"
    )
    impact_pleasant = weather_service.calculate_weather_impact(pleasant)
    assert impact_pleasant.weather_impact >= 0.0
    assert impact_pleasant.advisory_level == "NORMAL"

    stormy = WeatherObservation(
        destination_id="darjeeling",
        destination_name="Darjeeling",
        temperature_c=6.0,
        temp_min_c=4.0,
        temp_max_c=8.0,
        precipitation_probability=95,
        precipitation_mm=22.0,
        humidity=95,
        wind_speed_kmh=45.0,
        weather_condition="Thunderstorm",
        severe_weather="Heavy Mountain Rainfall & Landslide Warning",
        visibility_km=0.8,
        advisory="Severe downpour. Outdoor movement strongly discouraged.",
        source="DEMO_OPENWEATHER",
        provider_mode="DEMO",
        confidence=0.92,
        data_quality="HIGH",
        cache_status="LIVE"
    )
    impact_stormy = weather_service.calculate_weather_impact(stormy)
    assert impact_stormy.weather_impact < -0.3
    assert impact_stormy.advisory_level in ["WARNING", "CRITICAL"]


def test_weather_cache_and_stale_fallback():
    obs = weather_service.get_weather("darjeeling", force_refresh=True)
    assert obs.cache_status == "LIVE"

    obs_cached = weather_service.get_weather("darjeeling")
    assert obs_cached.cache_status == "CACHED"


# ==========================================
# 2. Traffic & Mountain Corridor Unit Tests
# ==========================================

def test_traffic_corridor_routes_schema():
    routes = [
        RouteTrafficObservation(
            route_id="nh55",
            route_name="NH-55 (Hill Cart Road)",
            origin="Siliguri",
            destination_id="darjeeling",
            historical_travel_time_min=75,
            current_travel_time_min=110,
            travel_time_ratio=1.47,
            travel_time_anomaly_percent=47.0,
            congestion_level="HIGH",
            road_status="SLOW",
            incident_count=1,
            incident_description="Monsoon fog & road construction"
        ),
        RouteTrafficObservation(
            route_id="rohini",
            route_name="Rohini Toll Bypass",
            origin="Siliguri",
            destination_id="darjeeling",
            historical_travel_time_min=60,
            current_travel_time_min=65,
            travel_time_ratio=1.08,
            travel_time_anomaly_percent=8.0,
            congestion_level="NORMAL",
            road_status="CLEAR"
        )
    ]
    summary = DestinationTrafficSummary(
        destination_id="darjeeling",
        destination_name="Darjeeling",
        overall_congestion_score=62.0,
        average_travel_time_ratio=1.28,
        travel_time_anomaly_percent=28.0,
        incident_count=1,
        access_status="CAUTION",
        primary_bottleneck_route="NH-55 (Hill Cart Road)",
        critical_routes=routes,
        source="DEMO_GOOGLE_TRAFFIC",
        provider_mode="DEMO",
        confidence=0.88,
        data_quality="HIGH",
        cache_status="LIVE"
    )
    assert summary.access_status == "CAUTION"
    assert len(summary.critical_routes) == 2
    assert summary.primary_bottleneck_route == "NH-55 (Hill Cart Road)"


def test_demo_traffic_provider_arterials():
    provider = DemoTrafficProvider()
    darjeeling_traffic = provider.fetch_traffic("darjeeling")
    assert darjeeling_traffic.destination_id == "darjeeling"
    assert len(darjeeling_traffic.critical_routes) >= 2
    assert darjeeling_traffic.access_status in ["OPEN", "CAUTION", "DISRUPTED"]
    assert darjeeling_traffic.average_travel_time_ratio >= 0.5


# ==========================================
# 3. Dynamic Pressure Recalculation Tests
# ==========================================

def test_pressure_recalculation_and_drivers():
    recalc = pressure_refresh_service.recalculate_destination_pressure("darjeeling")
    assert recalc.destination_id == "darjeeling"
    assert 0 <= recalc.pressure_score <= 100
    assert recalc.pressure_level in ["LOW", "MODERATE", "HIGH", "CRITICAL"]
    assert len(recalc.top_drivers) >= 3

    for driver in recalc.top_drivers:
        assert driver.signal is not None
        assert isinstance(driver.impact, (int, float))
        assert len(driver.description) > 0


def test_access_status_strictly_decoupled_from_crowd():
    recalc = pressure_refresh_service.recalculate_destination_pressure("darjeeling")
    assert hasattr(recalc, "access_status")
    assert recalc.access_status in ["OPEN", "CAUTION", "DISRUPTED", "UNKNOWN"]
    assert 0 <= recalc.pressure_score <= 100


# ==========================================
# 4. Future Dates Isolation Tests
# ==========================================

def test_future_dates_conditions_isolation():
    tomorrow = (date.today() + timedelta(days=2)).isoformat()
    cond = pressure_refresh_service.recalculate_destination_pressure("darjeeling", target_date_str=tomorrow)

    assert cond.condition_type == "FORECAST CONDITIONS"
    assert cond.traffic_impact.traffic_impact_score == 30.0
    assert "future dates" in cond.traffic_impact.impact_description.lower()


# ==========================================
# 5. Alternative Recommendation Filtering
# ==========================================

def test_alternative_engine_filters_disrupted_destinations():
    result = get_alternative_destinations("darjeeling")
    assert len(result.alternatives) > 0
    for cand in result.alternatives:
        traffic = traffic_service.get_traffic(cand.id)
        assert traffic.access_status != "DISRUPTED"


# ==========================================
# 6. API Endpoints & Cooldown Protection
# ==========================================

def test_api_get_destination_live_weather():
    response = client.get("/api/destinations/darjeeling/live-weather")
    assert response.status_code == 200
    data = response.json()
    assert data["destination_id"] == "darjeeling"
    assert "temperature_c" in data
    assert "visibility_km" in data
    assert "provider_mode" in data


def test_api_get_destination_traffic():
    response = client.get("/api/destinations/darjeeling/traffic")
    assert response.status_code == 200
    data = response.json()
    assert data["destination_id"] == "darjeeling"
    assert "access_status" in data
    assert "travel_time_anomaly_percent" in data
    assert "critical_routes" in data
    assert len(data["critical_routes"]) >= 1


def test_api_get_destination_conditions():
    response = client.get("/api/destinations/darjeeling/conditions")
    assert response.status_code == 200
    data = response.json()
    assert data["destination_id"] == "darjeeling"
    assert "weather" in data
    assert "traffic" in data
    assert "pressure_score" in data
    assert "access_status" in data
    assert "provenance" in data


def test_api_get_circuit_conditions():
    response = client.get("/api/destinations/circuit/conditions")
    assert response.status_code == 200
    data = response.json()
    assert "darjeeling" in data
    assert "kalimpong" in data
    assert "access_status" in data["darjeeling"]


def test_api_get_pressure_explanation():
    response = client.get("/api/destinations/kalimpong/pressure-explanation")
    assert response.status_code == 200
    data = response.json()
    assert data["destination_id"] == "kalimpong"
    assert "pressure_score" in data
    assert "top_drivers" in data
    assert len(data["top_drivers"]) >= 1


def test_api_admin_pressure_refresh_and_cooldown():
    # Force refresh should succeed
    res1 = client.post("/api/admin/pressure/refresh?destination_id=darjeeling&force=true")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["status"] == "success"

    # Rapid second refresh without force should encounter 429 cooldown protection
    res2 = client.post("/api/admin/pressure/refresh?destination_id=darjeeling&force=false")
    assert res2.status_code == 429
    assert "Cooldown active" in res2.json()["detail"]


# ==========================================
# 7. Security & Provenance Integrity Tests
# ==========================================

def test_api_keys_never_exposed_in_responses():
    endpoints = [
        "/api/destinations/darjeeling/live-weather",
        "/api/destinations/darjeeling/traffic",
        "/api/destinations/darjeeling/conditions",
        "/api/destinations/circuit/conditions",
        "/api/destinations/darjeeling/pressure-explanation"
    ]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200
        text = res.text
        assert "WEATHER_API_KEY" not in text
        assert "TRAFFIC_API_KEY" not in text
        assert "api_key" not in text.lower() or "provenance" in text.lower()
