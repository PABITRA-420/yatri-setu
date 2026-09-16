"""
Tests for Milestone 7D: Capacity-Aware Flow Management and Destination Network Intelligence.
Verifies:
1. Destination Network Model and Feasibility
2. Authoritative Capacity and Health Classifications
3. Redirection Absorption Logic (Access, Weather, Capacity, Pressure surge)
4. Upgraded Alternative Engine Pipeline
5. Flow Allocation Planner and Pressure Feedback Loop
6. Telemetry Non-Mutation Invariant
7. Admin Flow Simulation Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.network.service import destination_network_service
from app.services.network.repository import destination_network_repository
from app.services.network.schemas import DestinationNetworkEdge
from app.services.capacity.service import capacity_service, classify_capacity_health
from app.services.capacity.schemas import CapacityHealthStatus, CapacityDataStatus
from app.services.capacity.absorption import can_absorb_redirection
from app.services.alternative_engine import get_alternative_destinations
from app.services.flow.planner import flow_planner
from app.services.flow.schemas import FlowScenarioRequest
from app.services.demand_aggregation_service import demand_aggregation_service

client = TestClient(app)


class TestDestinationNetwork:
    def test_circuit_edges_exist(self):
        edges = destination_network_service.list_all_edges()
        assert len(edges) >= 14, "Expected at least 14 bidirectional Himalayan circuit edges"

    def test_outbound_edges_from_darjeeling(self):
        darj_edges = destination_network_service.get_outbound_edges("darjeeling")
        target_ids = {e.target_destination_id for e in darj_edges}
        assert "kalimpong" in target_ids
        assert "mirik" in target_ids
        assert "lava" in target_ids

    def test_route_feasibility(self):
        assert destination_network_service.is_route_feasible("darjeeling", "kalimpong") is True
        # Unknown destination route is not feasible
        assert destination_network_service.is_route_feasible("darjeeling", "nonexistent") is False

    def test_edge_corridor_mapping(self):
        edge = destination_network_service.get_edge("darjeeling", "kalimpong")
        assert edge is not None
        assert "rt-darj-nh55" in edge.corridor_ids
        assert edge.route_distance_km == 50.0
        assert edge.source == "STATIC_CONFIGURATION"
        assert edge.data_quality == "HIGH"


class TestCapacityService:
    def test_capacity_health_classification_thresholds(self):
        assert classify_capacity_health(0.30) == CapacityHealthStatus.HEALTHY
        assert classify_capacity_health(0.49) == CapacityHealthStatus.HEALTHY
        assert classify_capacity_health(0.50) == CapacityHealthStatus.LIMITED
        assert classify_capacity_health(0.74) == CapacityHealthStatus.LIMITED
        assert classify_capacity_health(0.75) == CapacityHealthStatus.HIGH_UTILIZATION
        assert classify_capacity_health(0.89) == CapacityHealthStatus.HIGH_UTILIZATION
        assert classify_capacity_health(0.90) == CapacityHealthStatus.FULL
        assert classify_capacity_health(0.98) == CapacityHealthStatus.FULL

    def test_destination_capacity_metrics(self):
        cap = capacity_service.get_destination_capacity("kalimpong")
        assert cap.destination_id == "kalimpong"
        assert cap.total_units > 0
        assert cap.available_units >= 0
        assert cap.occupied_units >= 0
        assert cap.total_units == cap.available_units + cap.occupied_units + cap.reserved_units
        assert 0.0 <= cap.occupancy_rate <= 1.0
        assert cap.unit_type == "rooms"
        assert cap.capacity_health in (
            CapacityHealthStatus.HEALTHY,
            CapacityHealthStatus.LIMITED,
            CapacityHealthStatus.HIGH_UTILIZATION,
            CapacityHealthStatus.FULL,
        )
        assert cap.capacity_data_status in (CapacityDataStatus.AVAILABLE, CapacityDataStatus.PARTIAL)
        assert cap.active_properties >= 1

    def test_homestay_repository_integration(self):
        # Kalimpong has verified homestays in authoritative repository
        cap = capacity_service.get_destination_capacity("kalimpong")
        assert cap.listed_properties >= 2
        assert cap.active_properties >= 2


class TestRedirectionAbsorption:
    def test_can_absorb_healthy_flow(self):
        res = can_absorb_redirection("kalimpong", expected_redirected_visitors=10)
        assert res.destination_id == "kalimpong"
        assert res.eligible is True
        assert res.remaining_capacity > 0
        assert res.projected_pressure >= res.current_pressure

    def test_cannot_absorb_extreme_overload(self):
        # Requesting 1000 visitors at small mountain settlement (Rishop)
        res = can_absorb_redirection("rishop", expected_redirected_visitors=1000)
        assert res.destination_id == "rishop"
        assert res.eligible is False
        assert "insufficient" in res.reason.lower() or "overload" in res.reason.lower() or "critical" in res.reason.lower()


class TestAlternativeEngineUpgrade:
    def test_alternative_destinations_include_m7d_fields(self):
        res = get_alternative_destinations("darjeeling")
        assert res.origin_destination_id == "darjeeling"
        assert len(res.alternatives) > 0

        first = res.alternatives[0]
        assert first.capacity_status in ("HEALTHY", "LIMITED", "HIGH_UTILIZATION", "FULL")
        assert first.available_capacity is not None
        assert first.access_status in ("OPEN", "CAUTION", "DISRUPTED")
        assert first.provenance == "REAL — YATRI SETU NETWORK"
        assert len(first.reasons_to_recommend) >= 2
        assert first.homestay_availability is not None

    def test_filters_out_origin_destination(self):
        res = get_alternative_destinations("kalimpong")
        alt_ids = [a.id for a in res.alternatives]
        assert "kalimpong" not in alt_ids


class TestFlowSimulation:
    def test_simulate_flow_optimal(self):
        req = FlowScenarioRequest(
            source_destination_id="darjeeling",
            affected_visitors=100,
            acceptance_rate=0.15
        )
        res = flow_planner.simulate_flow(req)

        assert res.scenario == "PLANNING_SCENARIO"
        assert res.source_destination["id"] == "darjeeling"
        assert res.affected_visitors == 100
        assert res.assumed_acceptance_rate == 0.15
        assert res.estimated_redirected_visitors == 15
        assert res.total_allocated_visitors > 0
        assert res.provenance == "SIMULATED — PLANNING SCENARIO"
        assert len(res.allocations) > 0

        # Check candidate allocations have simulated feedback
        for alloc in res.allocations:
            if alloc.allocated_visitors > 0:
                assert alloc.projected_pressure >= alloc.current_pressure
                assert alloc.absorption_status in ("ACCEPTED", "PARTIAL")

    def test_simulate_flow_capacity_limited(self):
        # Very high affected visitor count
        req = FlowScenarioRequest(
            source_destination_id="darjeeling",
            affected_visitors=5000,
            acceptance_rate=0.80
        )
        res = flow_planner.simulate_flow(req)
        assert res.status in ("FLOW_CAPACITY_LIMITED", "OPTIMAL")
        if res.status == "FLOW_CAPACITY_LIMITED":
            assert res.unallocated_visitors > 0
            assert len(res.warnings) > 0

    def test_telemetry_non_mutation_guarantee(self):
        # Verify demand telemetry is not modified by running simulation
        before_demand = demand_aggregation_service.get_destination_demand("kalimpong")
        before_booking = before_demand.normalized_booking_demand

        req = FlowScenarioRequest(
            source_destination_id="darjeeling",
            affected_visitors=300,
            acceptance_rate=0.50
        )
        flow_planner.simulate_flow(req)

        after_demand = demand_aggregation_service.get_destination_demand("kalimpong")
        assert after_demand.normalized_booking_demand == before_booking, "Telemetry was mutated by simulation!"


class TestAdminEndpoints:
    def test_admin_flow_simulate_api(self):
        payload = {
            "source_destination_id": "darjeeling",
            "affected_visitors": 80,
            "acceptance_rate": 0.20
        }
        resp = client.post("/api/admin/flow/simulate", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["scenario"] == "PLANNING_SCENARIO"
        assert data["estimated_redirected_visitors"] == 16
        assert len(data["allocations"]) > 0

    def test_admin_capacity_api(self):
        resp = client.get("/api/admin/capacity/kalimpong")
        assert resp.status_code == 200
        data = resp.json()
        assert data["destination_id"] == "kalimpong"
        assert data["total_units"] > 0
        assert data["capacity_health"] in ("HEALTHY", "LIMITED", "HIGH_UTILIZATION", "FULL")

    def test_admin_network_edges_api(self):
        resp = client.get("/api/admin/network/edges")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 14

        resp_filtered = client.get("/api/admin/network/edges?source_id=darjeeling")
        assert resp_filtered.status_code == 200
        data_filtered = resp_filtered.json()
        assert all(e["source_destination_id"] == "darjeeling" for e in data_filtered)
