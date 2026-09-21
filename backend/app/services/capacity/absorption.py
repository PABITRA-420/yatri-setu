"""
Redirection Absorption Logic for Yatri Setu (Milestone 7D).
Evaluates whether a candidate destination can safely absorb a redirected tourist flow
without overloading accommodation capacity, road corridors, or pressure limits.
"""

import math
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.services.capacity.schemas import CapacityHealthStatus
from app.services.capacity.service import capacity_service, classify_capacity_health
from app.services.traffic.service import traffic_service
from app.services.weather.service import weather_service
from app.services.crowd_engine_v2 import crowd_engine_v2


class RedirectionAbsorptionResult(BaseModel):
    eligible: bool = Field(..., description="Whether destination can safely absorb the redirection flow")
    destination_id: str = Field(..., description="Destination identifier")
    capacity_status: CapacityHealthStatus = Field(..., description="Current capacity health classification")
    available_capacity: int = Field(..., description="Available units (rooms)")
    estimated_incoming: int = Field(..., description="Incoming units requested by the redirection flow")
    remaining_capacity: int = Field(..., description="Units remaining after absorbing the flow")
    current_pressure: int = Field(..., description="Current pressure score (0-100)")
    projected_pressure: int = Field(..., description="Simulated pressure score after flow absorption (0-100)")
    access_status: str = Field(..., description="Road corridor status: OPEN, CAUTION, DISRUPTED")
    reason: str = Field(..., description="Transparent, explainable reason for eligibility decision")


def can_absorb_redirection(
    destination_id: str,
    expected_redirected_visitors: int
) -> RedirectionAbsorptionResult:
    """
    Evaluates whether candidate destination can absorb proposed incoming visitors.
    Converts visitors into accommodation units (assuming standard 2 visitors/room).
    Verifies capacity headroom, access corridor status, severe weather, and projected pressure surge.
    """
    clean_id = destination_id.lower().strip()
    cap = capacity_service.get_destination_capacity(clean_id)

    # Corridors & Road Safety
    traf = traffic_service.get_traffic(clean_id)
    access_status = traf.access_status or "OPEN"

    # Weather Suitability
    wth = weather_service.get_weather(clean_id)
    severe_weather = bool(wth.severe_weather and "warning" in wth.severe_weather.lower())

    # Current Pressure
    current_crowd = crowd_engine_v2.get_canonical_crowd_response(clean_id)
    current_pressure = current_crowd.crowd_score

    # Convert visitors to unit demand (2 visitors per room)
    units_needed = max(1, math.ceil(expected_redirected_visitors / 2)) if expected_redirected_visitors > 0 else 0

    # Projected post-redirection units and occupancy
    simulated_occupied = cap.occupied_units + units_needed
    simulated_occupancy_rate = simulated_occupied / max(1, cap.total_units)
    remaining_cap = cap.available_units - units_needed

    # Projected pressure surge calculation
    # Additional occupancy translates into local footfall and pressure surge
    occupancy_surge = max(0.0, simulated_occupancy_rate - cap.occupancy_rate)
    pressure_surge = int(round(occupancy_surge * 45.0))
    projected_pressure = min(100, current_pressure + pressure_surge)

    # 1. Safety Filter: Access Disruption
    if access_status == "DISRUPTED":
        return RedirectionAbsorptionResult(
            eligible=False,
            destination_id=clean_id,
            capacity_status=cap.capacity_health,
            available_capacity=cap.available_units,
            estimated_incoming=units_needed,
            remaining_capacity=remaining_cap,
            current_pressure=current_pressure,
            projected_pressure=projected_pressure,
            access_status=access_status,
            reason=f"Access corridor to {cap.destination_name} is currently disrupted."
        )

    # 2. Weather Filter: Severe Hazard
    if severe_weather:
        return RedirectionAbsorptionResult(
            eligible=False,
            destination_id=clean_id,
            capacity_status=cap.capacity_health,
            available_capacity=cap.available_units,
            estimated_incoming=units_needed,
            remaining_capacity=remaining_cap,
            current_pressure=current_pressure,
            projected_pressure=projected_pressure,
            access_status=access_status,
            reason=f"{cap.destination_name} has an active severe weather hazard warning."
        )

    # 3. Capacity Filter: Out of Capacity
    if cap.capacity_health == CapacityHealthStatus.FULL or remaining_cap < 0:
        return RedirectionAbsorptionResult(
            eligible=False,
            destination_id=clean_id,
            capacity_status=cap.capacity_health,
            available_capacity=cap.available_units,
            estimated_incoming=units_needed,
            remaining_capacity=remaining_cap,
            current_pressure=current_pressure,
            projected_pressure=projected_pressure,
            access_status=access_status,
            reason=(
                f"{cap.destination_name} has insufficient available units ({cap.available_units} available, "
                f"{units_needed} required) and cannot safely absorb this volume."
            )
        )

    # 4. Pressure Overload Filter: Existing Pressure Critical
    if current_pressure >= 80:
        return RedirectionAbsorptionResult(
            eligible=False,
            destination_id=clean_id,
            capacity_status=cap.capacity_health,
            available_capacity=cap.available_units,
            estimated_incoming=units_needed,
            remaining_capacity=remaining_cap,
            current_pressure=current_pressure,
            projected_pressure=projected_pressure,
            access_status=access_status,
            reason=f"{cap.destination_name} is already under elevated pressure ({current_pressure}/100)."
        )

    # 5. Pressure Feedback Loop: Projected Pressure Exceeds Threshold
    if projected_pressure >= 82:
        return RedirectionAbsorptionResult(
            eligible=False,
            destination_id=clean_id,
            capacity_status=cap.capacity_health,
            available_capacity=cap.available_units,
            estimated_incoming=units_needed,
            remaining_capacity=remaining_cap,
            current_pressure=current_pressure,
            projected_pressure=projected_pressure,
            access_status=access_status,
            reason=(
                f"Projected influx of {expected_redirected_visitors} visitors would drive {cap.destination_name} "
                f"pressure from {current_pressure} to critical {projected_pressure}/100."
            )
        )

    # Fully Eligible
    return RedirectionAbsorptionResult(
        eligible=True,
        destination_id=clean_id,
        capacity_status=cap.capacity_health,
        available_capacity=cap.available_units,
        estimated_incoming=units_needed,
        remaining_capacity=remaining_cap,
        current_pressure=current_pressure,
        projected_pressure=projected_pressure,
        access_status=access_status,
        reason=(
            f"{cap.destination_name} has healthy accommodation capacity ({cap.available_units} units available), "
            f"open corridor access, and safe projected pressure ({projected_pressure}/100)."
        )
    )
