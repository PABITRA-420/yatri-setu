"""
First-Party Demand Aggregation API Endpoints (Milestone 7A Hardening).
Exposes only aggregated, privacy-safe intelligence across monitored destinations and regional circuit.
Strictly does NOT return raw events, user IDs, session IDs, or personal information.
"""

from fastapi import APIRouter, HTTPException
from app.models.demand import DemandMetrics, CircuitDemandResponse, AdminDemandOverview
from app.services.demand_aggregation_service import demand_aggregation_service, CIRCUIT_DESTINATIONS

router = APIRouter(tags=["First-Party Demand Aggregation"])


@router.get("/demand/circuit", response_model=CircuitDemandResponse)
def get_circuit_demand():
    """
    Returns aggregated circuit-wide first-party demand metrics without raw events or PII.
    """
    return demand_aggregation_service.get_circuit_demand()


@router.get("/demand/{destination_id}", response_model=DemandMetrics)
def get_destination_demand(destination_id: str):
    """
    Returns aggregated destination-level first-party demand metrics without raw events or PII.
    """
    norm_id = destination_id.lower().strip()
    if norm_id not in CIRCUIT_DESTINATIONS:
        raise HTTPException(
            status_code=404,
            detail=f"Destination '{destination_id}' not found in demand circuit"
        )
    return demand_aggregation_service.get_destination_demand(norm_id)


@router.get("/admin/demand", response_model=AdminDemandOverview)
def get_admin_demand():
    """
    Returns administrative demand overview exposing aggregated funnels, trends, and provenance.
    Strictly excludes raw events, session IDs, and personal data.
    """
    return demand_aggregation_service.get_admin_overview()
