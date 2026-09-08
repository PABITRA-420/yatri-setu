"""
Pressure & Multi-Signal Intelligence Data Models for Yatri Setu.
Provides rich typing for Destination Pressure Layer, Command Center, and Simulation.
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class PressureLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DestinationSignal(BaseModel):
    signal_key: str
    signal_name: str
    weight: float = Field(..., ge=0.0, le=1.0)
    value: float = Field(..., ge=0.0, le=100.0)
    weighted_score: float
    available: bool = True
    source: str = "MOCK"
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    raw_value: Optional[float] = None
    unit: str = ""
    notes: str = ""


class PressureResponse(BaseModel):
    destination_id: str
    destination_name: str
    pressure_score: float = Field(..., ge=0.0, le=100.0)
    pressure_level: PressureLevel
    color_code: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_percent: int
    signals_available: int
    total_signals: int
    signals: List[DestinationSignal]
    advisory: str
    recommended_action: str
    carrying_capacity_percent: float
    peak_hours: str
    best_time_to_visit: str
    timestamp: str


class PressureDayForecast(BaseModel):
    date: str
    day_name: str
    predicted_pressure: float = Field(..., ge=0.0, le=100.0)
    pressure_level: PressureLevel
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    key_driver: str
    is_weekend: bool = False
    is_holiday: bool = False


class ForecastResponse(BaseModel):
    destination_id: str
    destination_name: str
    current_pressure: float
    forecast_days: List[PressureDayForecast]
    trend: str  # "RISING", "FALLING", "STABLE"
    summary: str


class InterventionSimulationRequest(BaseModel):
    destination_id: str
    intervention_type: str = Field(
        "entry_quota",
        description="Type: entry_quota, shuttle_diversion, surge_permit_fee, homestay_incentive"
    )
    intensity_percent: float = Field(25.0, ge=5.0, le=75.0, description="Intervention policy strength")


class BeneficiaryDestination(BaseModel):
    destination_id: str
    destination_name: str
    redirected_visitors: int
    estimated_revenue_gain_inr: float
    capacity_remaining_percent: float


class InterventionSimulationResult(BaseModel):
    destination_id: str
    destination_name: str
    intervention_type: str
    intensity_percent: float
    original_pressure: float
    simulated_pressure: float
    pressure_reduction_percent: float
    redirected_tourists_count: int
    beneficiary_destinations: List[BeneficiaryDestination]
    total_rural_revenue_generated_inr: float
    policy_summary: str
    is_simulation: bool = True
    simulation_notes: str


class DestinationPressureOverview(BaseModel):
    destination_id: str
    destination_name: str
    state: str
    pressure_score: float
    pressure_level: PressureLevel
    confidence_score: float
    occupancy_percent: float
    active_events_count: int
    traffic_status: str
    is_chokepoint: bool


class FlowDistributionSummary(BaseModel):
    origin_destination_id: str
    origin_destination_name: str
    origin_pressure_score: float
    redirected_travelers_7d: int
    dispersal_efficiency_percent: float
    top_absorber_id: str
    top_absorber_name: str
    economic_impact_inr_7d: float


class CommandCenterData(BaseModel):
    total_destinations_monitored: int
    critical_pressure_count: int
    high_pressure_count: int
    moderate_pressure_count: int
    low_pressure_count: int
    total_active_signals: int
    average_data_confidence: float
    destinations: List[DestinationPressureOverview]
    flow_summary: List[FlowDistributionSummary]
    system_status: str = "OPERATIONAL (MULTI-SIGNAL V2)"
    last_updated: str
