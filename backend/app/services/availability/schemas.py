"""
Availability Schemas for Yatri Setu (Milestone 7E).
Defines date-aware accommodation availability, inventory snapshots, and provenance.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AvailabilityStatus(str, Enum):
    AVAILABLE = "AVAILABLE"   # > 25% units available
    LIMITED = "LIMITED"       # 1 - 25% units available
    FULL = "FULL"             # 0 units available
    UNKNOWN = "UNKNOWN"       # Incomplete or unverified inventory


class HomestayAvailabilitySnapshot(BaseModel):
    homestay_id: str = Field(..., description="Unique canonical homestay identifier")
    destination_id: str = Field(..., description="Destination identifier (e.g. kalimpong)")
    date: str = Field(..., description="Target date in YYYY-MM-DD format")
    total_units: int = Field(..., description="Total room inventory allocated to homestay")
    available_units: int = Field(..., description="Units currently available for check-in on this date")
    occupied_units: int = Field(..., description="Units currently booked on this date")
    reserved_units: int = Field(0, description="Units held for local contingency")
    availability_status: AvailabilityStatus = Field(..., description="Availability classification")
    source: str = Field("AUTHORITATIVE_HOMESTAY_LEDGER", description="Provenance source")
    provider_mode: str = Field("REAL", description="Provider mode: REAL, SIMULATED, MOCK")
    data_quality: str = Field("HIGH", description="Data quality rating")
    updated_at: str = Field(..., description="ISO 8601 timestamp")


class DestinationAvailabilitySnapshot(BaseModel):
    destination_id: str = Field(..., description="Destination identifier")
    destination_name: str = Field(..., description="Human-readable destination name")
    date: str = Field(..., description="Target date in YYYY-MM-DD format")
    total_units: int = Field(..., description="Total regional accommodation capacity (rooms)")
    available_units: int = Field(..., description="Total units available across active properties on this date")
    occupied_units: int = Field(..., description="Total units booked on this date")
    occupancy_rate: float = Field(..., ge=0.0, le=1.0, description="Occupancy ratio on this date")
    availability_status: AvailabilityStatus = Field(..., description="Regional availability classification")
    data_quality: str = Field("HIGH", description="Data quality rating")
    source: str = Field("YATRI_SETU_AVAILABILITY_LEDGER", description="Provenance source")
    provider_mode: str = Field("REAL", description="Provider mode")
    updated_at: str = Field(..., description="ISO 8601 timestamp")
