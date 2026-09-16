"""
Flow Simulation Schemas for Yatri Setu (Milestone 7D).
Defines planning scenario models for crowd flow allocation and pressure feedback loop.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class CandidateAllocation(BaseModel):
    destination_id: str = Field(..., description="Target candidate destination identifier")
    destination_name: str = Field(..., description="Human-readable destination name")
    allocated_visitors: int = Field(..., description="Projected visitors allocated to this candidate")
    allocation_percentage: float = Field(..., description="Percentage of total redirected flow allocated")
    current_pressure: int = Field(..., description="Current pressure score (0-100)")
    projected_pressure: int = Field(..., description="Simulated pressure score after absorbing allocation (0-100)")
    capacity_status: str = Field(..., description="Capacity health classification: HEALTHY, LIMITED, FULL")
    absorption_status: str = Field(..., description="Absorption outcome: ACCEPTED, PARTIAL, REJECTED")
    available_capacity: int = Field(..., description="Available accommodation units before allocation")
    remaining_capacity: int = Field(..., description="Remaining units after absorbing allocation")
    notes: str = Field(..., description="Diagnostic note detailing allocation rationale or constraints")


class FlowScenarioRequest(BaseModel):
    source_destination_id: str = Field(..., description="Overcrowded origin destination (e.g., darjeeling)")
    affected_visitors: int = Field(..., ge=1, le=10000, description="Estimated total affected visitors at source")
    date: Optional[str] = Field(None, description="Optional simulation target date (YYYY-MM-DD)")
    acceptance_rate: Optional[float] = Field(
        None,
        ge=0.01,
        le=1.0,
        description="Optional simulation acceptance rate override (defaults to REDIRECTION_ACCEPTANCE_RATE=0.15)"
    )


class FlowScenarioResponse(BaseModel):
    scenario: str = Field("PLANNING_SCENARIO", description="Identifies this as a simulated planning scenario")
    source_destination: Dict[str, Any] = Field(..., description="Source destination summary and pressure")
    affected_visitors: int = Field(..., description="Gross affected visitor headcount at source")
    assumed_acceptance_rate: float = Field(..., description="Model acceptance rate assumption (e.g. 0.15)")
    estimated_redirected_visitors: int = Field(..., description="Net visitors seeking alternative routing")
    total_allocated_visitors: int = Field(..., description="Total visitors successfully distributed to network")
    unallocated_visitors: int = Field(..., description="Visitors that could not be absorbed without overloading")
    status: str = Field(
        ...,
        description="Scenario result status: OPTIMAL, FLOW_CAPACITY_LIMITED, NO_ELIGIBLE_DESTINATIONS"
    )
    allocations: List[CandidateAllocation] = Field(
        default_factory=list,
        description="Per-destination distribution breakdown"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Operational alerts if network capacity is constrained or routes disrupted"
    )
    provenance: str = Field(
        "SIMULATED — PLANNING SCENARIO",
        description="Explicit provenance guaranteeing this is not live first-party visitor telemetry"
    )
    generated_at: str = Field(..., description="ISO 8601 generation timestamp")
