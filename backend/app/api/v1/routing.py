"""
Routing API endpoints for Yatri Setu (Milestone 8A).
Exposes road distance, travel ETA, transit mode, and GeoJSON geometry.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Query, HTTPException
from app.services.routing.service import routing_service
from app.services.routing.schemas import RouteCalculationResponse
from app.services.routing.coordinates import CIRCUIT_COORDINATES, CIRCUIT_NAMES

router = APIRouter(prefix="/routing", tags=["Road Routing & Transit Advisor"])


@router.get("/route", response_model=RouteCalculationResponse)
def get_route(
    origin: str = Query(..., description="Origin circuit destination id (e.g. 'darjeeling')"),
    destination: str = Query(..., description="Target circuit destination id (e.g. 'kalimpong')"),
    transit_mode: Optional[str] = Query(None, description="Preferred transit mode"),
    force_refresh: bool = Query(False, description="Bypass cache")
):
    """
    Returns road routing estimates, travel duration, road conditions, and GeoJSON geometry.
    Uses OSRM OpenStreetMap routing with high-fidelity Demo and Haversine fallbacks.
    """
    try:
        return routing_service.calculate_route(
            origin_id=origin,
            destination_id=destination,
            transit_mode=transit_mode,
            force_refresh=force_refresh
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Routing calculation failed: {ex}")


@router.get("/destinations", response_model=Dict[str, Any])
def get_circuit_routing_nodes():
    """
    Returns canonical coordinate nodes and metadata for the 6 Eastern Himalayan circuit destinations.
    """
    nodes = []
    for dest_id, (lat, lon) in CIRCUIT_COORDINATES.items():
        nodes.append({
            "id": dest_id,
            "name": CIRCUIT_NAMES.get(dest_id, dest_id.title()),
            "latitude": lat,
            "longitude": lon,
            "coordinates": [lon, lat]  # GeoJSON [lng, lat]
        })
    return {
        "circuit": "Eastern Himalayas (Darjeeling-Kalimpong-Lava-Lolegaon-Rishop-Mirik)",
        "count": len(nodes),
        "nodes": nodes
    }
