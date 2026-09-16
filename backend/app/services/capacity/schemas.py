"""
Capacity Schemas for Yatri Setu (Milestone 7D).
Defines normalized accommodation capacity, health classifications, and provenance.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CapacityHealthStatus(str, Enum):
    HEALTHY = "HEALTHY"                     # < 50% occupancy
    LIMITED = "LIMITED"                     # 50% - 75% occupancy
    HIGH_UTILIZATION = "HIGH_UTILIZATION"   # 75% - 90% occupancy
    FULL = "FULL"                           # > 90% occupancy
    UNKNOWN = "UNKNOWN"                     # Incomplete or missing inventory data


class CapacityDataStatus(str, Enum):
    AVAILABLE = "AVAILABLE"   # Complete room-level and booking ledger data
    PARTIAL = "PARTIAL"       # Verified property listings with estimated room allocation
    UNKNOWN = "UNKNOWN"       # No local listings or unverified homestays


class CapacityConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNKNOWN = "UNKNOWN"


class DestinationCapacity(BaseModel):
    destination_id: str = Field(..., description="Destination identifier (e.g., kalimpong)")
    destination_name: str = Field(..., description="Human-readable destination name")
    listed_properties: int = Field(..., description="Total homestays registered in repository")
    active_properties: int = Field(..., description="Verified & published properties accepting bookings")
    total_units: int = Field(..., description="Total accommodation units (rooms)")
    available_units: int = Field(..., description="Units currently available for check-in")
    occupied_units: int = Field(..., description="Units currently booked or occupied")
    reserved_units: int = Field(0, description="Units held for contingency or offline allocation")
    occupancy_rate: float = Field(..., ge=0.0, le=1.0, description="Current occupancy ratio (0.0 to 1.0)")
    estimated_daily_host_capacity: int = Field(
        ...,
        description="Estimated max tourist headcount hostable per day across active properties"
    )
    capacity_health: CapacityHealthStatus = Field(
        ...,
        description="Operational capacity health classification: HEALTHY, LIMITED, HIGH_UTILIZATION, FULL"
    )
    capacity_data_status: CapacityDataStatus = Field(
        ...,
        description="Completeness of capacity data: AVAILABLE, PARTIAL, UNKNOWN"
    )
    capacity_confidence: CapacityConfidence = Field(
        ...,
        description="Confidence derived from data provenance and completeness"
    )
    unit_type: str = Field(
        "rooms",
        description="Standardized unit representation: 'rooms' across all accommodation facilities"
    )
    last_updated: str = Field(..., description="ISO 8601 timestamp of capacity calculation")
    source: str = Field("HOMESTAY_REPOSITORY_INTEGRATION", description="Provenance source")
    provider_mode: str = Field("REAL", description="Provider mode: REAL, SIMULATED, MOCK")
    data_quality: str = Field("HIGH", description="Data quality rating")
