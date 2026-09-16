"""
Destination Network Models for Yatri Setu (Milestone 7D).
Defines normalized relationships and corridors between destinations in the circuit.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class DestinationNetworkEdge(BaseModel):
    source_destination_id: str = Field(..., description="Origin destination ID (e.g., darjeeling)")
    target_destination_id: str = Field(..., description="Target destination ID (e.g., kalimpong)")
    route_distance_km: float = Field(..., description="Actual road distance in kilometers")
    typical_travel_time_min: int = Field(..., description="Typical travel time in minutes under normal conditions")
    alternative_type: str = Field(
        ...,
        description="Relationship type: NEIGHBORING_CIRCUIT, CULTURAL_ALTERNATIVE, NATURE_SANCTUARY, TRANQUIL_RETREAT"
    )
    corridor_ids: List[str] = Field(
        default_factory=list,
        description="Traffic corridor IDs connecting source and target"
    )
    seasonality: str = Field(
        "ALL_SEASON",
        description="Seasonality tag: ALL_SEASON, MONSOON_CAUTION, WINTER_SNOW_CAUTION"
    )
    transfer_feasibility: str = Field(
        "HIGH",
        description="Transfer feasibility level: HIGH, MODERATE, LOW, DISRUPTED"
    )
    active: bool = Field(True, description="Whether this edge is currently active in the network")
    source: str = Field("STATIC_CONFIGURATION", description="Provenance of edge configuration")
    data_quality: str = Field("HIGH", description="Data quality rating of the edge information")
