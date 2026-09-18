"""
Comprehensive tests for Yatri Setu Milestone 8A Routing Service and API.
Tests OSRM, Demo, and Fallback providers, coordinate mapping, caching, and provenance.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.routing.schemas import RouteCalculationResponse
from app.services.routing.demo_provider import DemoRouteProvider
from app.services.routing.fallback_provider import FallbackRouteProvider
from app.services.routing.osrm_provider import OSRMRouteProvider
from app.services.routing.service import RoutingService, routing_service
from app.services.routing.coordinates import CIRCUIT_COORDINATES

client = TestClient(app)


class TestRoutingProviders:
    """Test individual routing providers in isolation."""

    def test_demo_provider_curated_routes(self):
        provider = DemoRouteProvider()

        # Darjeeling -> Kalimpong
        res = provider.calculate_route("darjeeling", "kalimpong")
        assert res.origin_destination_id == "darjeeling"
        assert res.destination_destination_id == "kalimpong"
        assert res.distance_km == 50.0
        assert res.duration_minutes == 110
        assert res.is_road_distance is True
        assert "DEMO MODE" in res.provenance_label
        assert len(res.route_geometry.coordinates) >= 5
        # Verify first and last coordinates match destination coordinates
        first_pt = res.route_geometry.coordinates[0]
        last_pt = res.route_geometry.coordinates[-1]
        assert abs(first_pt[1] - CIRCUIT_COORDINATES["darjeeling"][0]) < 0.05
        assert abs(last_pt[1] - CIRCUIT_COORDINATES["kalimpong"][0]) < 0.05

    def test_demo_provider_darjeeling_to_lava(self):
        provider = DemoRouteProvider()
        res = provider.calculate_route("darjeeling", "lava")
        assert res.distance_km == 78.0
        assert res.duration_minutes == 160
        assert res.is_road_distance is True
        assert len(res.route_geometry.coordinates) >= 4

    def test_demo_provider_kalimpong_to_lava(self):
        provider = DemoRouteProvider()
        res = provider.calculate_route("kalimpong", "lava")
        assert res.distance_km == 32.0
        assert res.duration_minutes == 75
        assert res.is_road_distance is True

    def test_demo_provider_intra_town(self):
        provider = DemoRouteProvider()
        res = provider.calculate_route("darjeeling", "darjeeling")
        assert res.distance_km < 10.0
        assert res.is_road_distance is True
        assert "Local Circuit" in res.destination_name

    def test_demo_provider_unknown_destination_raises(self):
        provider = DemoRouteProvider()
        with pytest.raises(ValueError, match="Unknown origin destination"):
            provider.calculate_route("mumbai", "kalimpong")
        with pytest.raises(ValueError, match="Unknown destination"):
            provider.calculate_route("darjeeling", "goa")

    def test_fallback_haversine_provider(self):
        provider = FallbackRouteProvider()
        res = provider.calculate_route("darjeeling", "kalimpong")

        # Straight-line distance between Darjeeling (27.0410, 88.2663) and Kalimpong (27.0594, 88.4695) is ~20 km
        assert 15.0 < res.distance_km < 30.0
        assert res.is_road_distance is False
        assert "FALLBACK — ROUTING UNAVAILABLE" in res.provenance_label
        assert "HAVERSINE" in res.provenance_label
        assert len(res.route_geometry.coordinates) == 2

    def test_osrm_provider_error_handling(self):
        provider = OSRMRouteProvider(base_url="http://invalid-unreachable-osrm-host:9999", timeout_seconds=0.5)
        with pytest.raises(Exception):
            provider.calculate_route("darjeeling", "kalimpong")


class TestRoutingServiceCoordinator:
    """Test RoutingService fallback cascade, caching, and traffic enrichment."""

    def test_routing_service_fallback_cascade_on_osrm_failure(self):
        service = RoutingService(ttl_seconds=60)
        broken_osrm = OSRMRouteProvider(base_url="http://non-existent-osrm.internal", timeout_seconds=0.1)
        service.set_provider(broken_osrm)

        # Should NOT raise an exception, should smoothly fall back to demo
        res = service.calculate_route("darjeeling", "kalimpong", force_refresh=True)
        assert res is not None
        assert res.distance_km == 50.0
        assert res.is_road_distance is True
        assert res.destination_destination_id == "kalimpong"

    def test_routing_service_caching(self):
        service = RoutingService(ttl_seconds=60)
        res1 = service.calculate_route("kalimpong", "lava", force_refresh=True)
        res2 = service.calculate_route("kalimpong", "lava", force_refresh=False)
        assert res1.distance_km == res2.distance_km
        assert res1.duration_minutes == res2.duration_minutes


class TestRoutingAPIEndpoints:
    """Test FastAPI routing endpoints."""

    def test_get_route_endpoint_success(self):
        resp = client.get("/api/v1/routing/route?origin=darjeeling&destination=kalimpong")
        assert resp.status_code == 200
        data = resp.json()
        assert data["origin_destination_id"] == "darjeeling"
        assert data["destination_destination_id"] == "kalimpong"
        assert 48.0 <= data["distance_km"] <= 55.0
        assert 45 <= data["duration_minutes"] <= 140
        assert data["is_road_distance"] is True
        assert "coordinates" in data["route_geometry"]
        assert len(data["route_geometry"]["coordinates"]) >= 2
        assert "provenance_label" in data

    def test_get_route_darjeeling_to_lava(self):
        resp = client.get("/api/v1/routing/route?origin=darjeeling&destination=lava")
        assert resp.status_code == 200
        data = resp.json()
        assert 75.0 <= data["distance_km"] <= 85.0
        assert 65 <= data["duration_minutes"] <= 180

    def test_get_route_kalimpong_to_lava(self):
        resp = client.get("/api/v1/routing/route?origin=kalimpong&destination=lava")
        assert resp.status_code == 200
        data = resp.json()
        assert 30.0 <= data["distance_km"] <= 36.0

    def test_get_route_unknown_destination_returns_404(self):
        resp = client.get("/api/v1/routing/route?origin=darjeeling&destination=tokyo")
        assert resp.status_code == 404
        assert "Unknown destination" in resp.json()["detail"]

    def test_get_circuit_destinations_endpoint(self):
        resp = client.get("/api/v1/routing/destinations")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 6
        node_ids = [n["id"] for n in data["nodes"]]
        assert "darjeeling" in node_ids
        assert "kalimpong" in node_ids
        assert "lava" in node_ids
        assert "lolegaon" in node_ids
        assert "rishop" in node_ids
        assert "mirik" in node_ids

    def test_health_check_includes_routing_provider(self):
        resp = client.get("/api/health?detailed=true")
        assert resp.status_code == 200
        data = resp.json()
        assert "routing" in data["providers"]
        routing_info = data["providers"]["routing"]
        assert "provider" in routing_info
        assert "mode" in routing_info
        assert "available" in routing_info
        assert "provenance" in routing_info
