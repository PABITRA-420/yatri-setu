"""
Flow Allocation Planner for Yatri Setu (Milestone 7D).
Simulates tourist redirection flow across destination network edges, calculating
headroom, capacity absorption, and projected pressure surges without modifying real telemetry.
"""

from datetime import datetime
import math
from typing import Dict, List, Any, Optional

from app.core.config import settings
from app.data.seed_data import DESTINATIONS_DATA
from app.services.network.service import destination_network_service
from app.services.capacity.service import capacity_service
from app.services.capacity.absorption import can_absorb_redirection
from app.services.capacity.schemas import CapacityHealthStatus
from app.services.crowd_engine_v2 import crowd_engine_v2
from app.services.flow.schemas import (
    CandidateAllocation,
    FlowScenarioRequest,
    FlowScenarioResponse,
)


class FlowAllocationPlanner:
    def simulate_flow(self, request: FlowScenarioRequest) -> FlowScenarioResponse:
        """
        Executes a planning scenario:
        1. Identifies source destination and current pressure.
        2. Applies redirection acceptance rate assumption.
        3. Identifies reachable network candidates from destination_network_service.
        4. Calculates candidate absorption headroom and projected pressure feedback.
        5. Computes multi-candidate flow allocation.
        """
        src_id = request.source_destination_id.lower().strip()
        src_dest = next((d for d in DESTINATIONS_DATA if d["id"] == src_id), None)
        src_name = src_dest["name"] if src_dest else src_id.capitalize()

        src_crowd = crowd_engine_v2.get_canonical_crowd_response(src_id)
        src_pressure = src_crowd.crowd_score

        # Model acceptance assumption
        rate = request.acceptance_rate if request.acceptance_rate is not None else settings.REDIRECTION_ACCEPTANCE_RATE
        affected = request.affected_visitors
        estimated_redirected = max(1, int(round(affected * rate)))

        # Find reachable candidates from network graph
        candidate_ids = destination_network_service.get_candidate_destinations(src_id)
        # Fallback to all circuit members except origin if graph has no edges
        if not candidate_ids:
            candidate_ids = [d["id"] for d in DESTINATIONS_DATA if d["id"] != src_id]

        allocations: List[CandidateAllocation] = []
        warnings: List[str] = []

        # Evaluate absorption potential for each candidate
        evaluated_candidates = []
        for c_id in candidate_ids:
            c_dest = next((d for d in DESTINATIONS_DATA if d["id"] == c_id), None)
            c_name = c_dest["name"] if c_dest else c_id.capitalize()
            c_cap = capacity_service.get_destination_capacity(c_id)
            c_crowd = crowd_engine_v2.get_canonical_crowd_response(c_id)

            # Max visitors this candidate could theoretically accept before reaching 80 pressure or running out of rooms
            # Available rooms * 2 guests = max capacity headcount
            max_headroom_visitors = max(0, c_cap.available_units * 2)
            # Pressure headroom: every 2 visitors adds approx 1 point of pressure
            pressure_headroom = max(0, (80 - c_crowd.crowd_score) * 2)
            absorbable_max = min(max_headroom_visitors, pressure_headroom)

            # Route feasibility check
            feasible = destination_network_service.is_route_feasible(src_id, c_id)

            evaluated_candidates.append({
                "id": c_id,
                "name": c_name,
                "capacity": c_cap,
                "current_pressure": c_crowd.crowd_score,
                "absorbable_max": absorbable_max,
                "feasible": feasible,
            })

        # Filter candidates that can receive flow
        eligible_candidates = [
            c for c in evaluated_candidates
            if c["feasible"] and c["absorbable_max"] > 0 and c["capacity"].capacity_health != CapacityHealthStatus.FULL
        ]

        total_absorbable = sum(c["absorbable_max"] for c in eligible_candidates)
        remaining_to_allocate = estimated_redirected
        total_allocated = 0

        if not eligible_candidates:
            status = "NO_ELIGIBLE_DESTINATIONS"
            warnings.append(
                f"No eligible receiving destinations available from {src_name}. "
                "Corridors disrupted, severe weather active, or candidate accommodations full."
            )
            for c in evaluated_candidates:
                allocations.append(CandidateAllocation(
                    destination_id=c["id"],
                    destination_name=c["name"],
                    allocated_visitors=0,
                    allocation_percentage=0.0,
                    current_pressure=c["current_pressure"],
                    projected_pressure=c["current_pressure"],
                    capacity_status=c["capacity"].capacity_health.value,
                    absorption_status="REJECTED",
                    available_capacity=c["capacity"].available_units,
                    remaining_capacity=c["capacity"].available_units,
                    notes=f"Ineligible: insufficient capacity headroom ({c['absorbable_max']} max) or route caution."
                ))
        else:
            # Proportional distribution based on absorbable headroom
            for c in eligible_candidates:
                if total_absorbable > 0:
                    weight = c["absorbable_max"] / total_absorbable
                else:
                    weight = 1.0 / len(eligible_candidates)

                target_allocation = int(round(estimated_redirected * weight))
                actual_allocation = min(target_allocation, c["absorbable_max"], remaining_to_allocate)

                # Evaluate single candidate absorption check with actual allocation
                absorption_check = can_absorb_redirection(c["id"], actual_allocation)

                # Simulated pressure surge
                surge = int(round((actual_allocation / max(1, c["capacity"].estimated_daily_host_capacity)) * 30.0))
                sim_proj_pressure = min(100, c["current_pressure"] + surge)

                allocated_rooms = math.ceil(actual_allocation / 2) if actual_allocation > 0 else 0
                rem_units = max(0, c["capacity"].available_units - allocated_rooms)

                if actual_allocation == target_allocation and actual_allocation > 0:
                    abs_status = "ACCEPTED"
                elif actual_allocation > 0:
                    abs_status = "PARTIAL"
                else:
                    abs_status = "REJECTED"

                total_allocated += actual_allocation
                remaining_to_allocate -= actual_allocation

                allocations.append(CandidateAllocation(
                    destination_id=c["id"],
                    destination_name=c["name"],
                    allocated_visitors=actual_allocation,
                    allocation_percentage=round((actual_allocation / max(1, estimated_redirected)) * 100.0, 1),
                    current_pressure=c["current_pressure"],
                    projected_pressure=sim_proj_pressure,
                    capacity_status=c["capacity"].capacity_health.value,
                    absorption_status=abs_status,
                    available_capacity=c["capacity"].available_units,
                    remaining_capacity=rem_units,
                    notes=absorption_check.reason
                ))

            # Add non-eligible candidates to allocation list for full visibility
            non_eligible = [c for c in evaluated_candidates if c not in eligible_candidates]
            for c in non_eligible:
                allocations.append(CandidateAllocation(
                    destination_id=c["id"],
                    destination_name=c["name"],
                    allocated_visitors=0,
                    allocation_percentage=0.0,
                    current_pressure=c["current_pressure"],
                    projected_pressure=c["current_pressure"],
                    capacity_status=c["capacity"].capacity_health.value,
                    absorption_status="REJECTED",
                    available_capacity=c["capacity"].available_units,
                    remaining_capacity=c["capacity"].available_units,
                    notes="Excluded from allocation: capacity saturated or elevated existing pressure."
                ))

            # Sort allocations deterministically by allocated_visitors desc, then projected pressure asc
            allocations.sort(key=lambda a: (-a.allocated_visitors, a.projected_pressure))

            if total_allocated < estimated_redirected:
                status = "FLOW_CAPACITY_LIMITED"
                unallocated = estimated_redirected - total_allocated
                warnings.append(
                    f"Aggregate circuit receiving capacity limited. Could only safely allocate {total_allocated} of "
                    f"{estimated_redirected} estimated redirected visitors ({unallocated} unallocated)."
                )
            else:
                status = "OPTIMAL"

        unallocated_count = max(0, estimated_redirected - total_allocated)

        return FlowScenarioResponse(
            scenario="PLANNING_SCENARIO",
            source_destination={
                "id": src_id,
                "name": src_name,
                "current_pressure": src_pressure,
                "crowd_level": src_crowd.crowd_level.value,
            },
            affected_visitors=affected,
            assumed_acceptance_rate=rate,
            estimated_redirected_visitors=estimated_redirected,
            total_allocated_visitors=total_allocated,
            unallocated_visitors=unallocated_count,
            status=status,
            allocations=allocations,
            warnings=warnings,
            provenance="SIMULATED — PLANNING SCENARIO",
            generated_at=datetime.utcnow().isoformat()
        )


flow_planner = FlowAllocationPlanner()
