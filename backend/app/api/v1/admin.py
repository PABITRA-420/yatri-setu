"""
Admin Command Center & Intervention Simulation API Endpoints for Yatri Setu.
Provides comprehensive oversight of destination stress, multi-signal telemetry,
flow dispersal efficiency, and policy intervention simulations.
"""
from typing import List, Optional
from fastapi import APIRouter, Query
from app.models.pressure import (
    CommandCenterData,
    DestinationPressureOverview,
    FlowDistributionSummary,
    InterventionSimulationRequest,
    InterventionSimulationResult
)
from app.services.crowd_engine_v2 import crowd_engine_v2

router = APIRouter(prefix="/admin", tags=["Admin Command Center"])


@router.get("/command-center", response_model=CommandCenterData)
def get_command_center_data():
    """
    Returns unified telemetry across all monitored destinations,
    signal statuses, average confidence, and regional flow redistribution.
    """
    return crowd_engine_v2.get_command_center_overview()


@router.get("/destinations/pressure", response_model=List[DestinationPressureOverview])
def list_destinations_pressure():
    """
    Returns tabular destination pressure status across the regional circuit.
    """
    overview = crowd_engine_v2.get_command_center_overview()
    return overview.destinations


@router.get("/flow", response_model=List[FlowDistributionSummary])
def get_flow_redistribution():
    """
    Returns flow distribution metrics, tourist redirections, and rural economic uplift.
    """
    overview = crowd_engine_v2.get_command_center_overview()
    return overview.flow_summary


@router.post("/intervention-simulation", response_model=InterventionSimulationResult)
def simulate_policy_intervention(req: InterventionSimulationRequest):
    """
    Simulate impact of administrative policy levers (entry quotas, shuttle diversions, etc.)
    on origin destination pressure and rural receiver clusters.
    """
    return crowd_engine_v2.simulate_intervention(
        destination_id=req.destination_id,
        intervention_type=req.intervention_type,
        intensity_percent=req.intensity_percent
    )


@router.get("/intervention-simulation", response_model=InterventionSimulationResult)
def simulate_policy_intervention_get(
    destination_id: str = Query("darjeeling", description="Target destination"),
    intervention_type: str = Query("entry_quota", description="Policy intervention type"),
    intensity_percent: float = Query(25.0, ge=5.0, le=75.0, description="Intervention intensity %")
):
    """
    GET convenience endpoint for running policy intervention simulations.
    """
    return crowd_engine_v2.simulate_intervention(
        destination_id=destination_id,
        intervention_type=intervention_type,
        intensity_percent=intensity_percent
    )



from app.models.observation import (
    ForecastPerformance,
    ForecastPerformanceV2,
    ProviderStatus,
    ProviderStatusV2
)
from app.services.forecast_accuracy_engine import forecast_accuracy_engine


@router.get("/forecast-performance", response_model=ForecastPerformance)
def get_forecast_performance():
    """
    Returns predictive accuracy metrics (MAE, RMSE, directional accuracy, hit-rate, grade)
    evaluating historical forecasts against actual crowd observations.
    """
    return forecast_accuracy_engine.get_performance()


from app.models.dataset_evaluation import DataQualityReport, BaselineEvaluationReport
from app.services.data_quality_service import data_quality_service
from app.services.baseline_evaluation import baseline_evaluation_service


@router.get("/providers", response_model=List[ProviderStatus])
def get_data_providers():
    """
    Returns operational status, trust modes (MOCK/REAL/CACHED),
    weights, and reliability of all 8 data source providers.
    """
    return crowd_engine_v2.get_provider_statuses()


@router.get("/providers/status", response_model=List[ProviderStatusV2])
def get_data_providers_status():
    """
    Returns UI-aligned live operational status, trust modes (MOCK/REAL/CACHED),
    confidence, and latency of all 8 data source providers for the Provider Trust Strip.
    """
    return crowd_engine_v2.get_provider_statuses_v2()


@router.get("/forecast-performance/baseline", response_model=BaselineEvaluationReport)
def get_baseline_forecast_evaluation():
    """
    Returns empirical evaluation report benchmarking the deterministic rule-based
    Crowd Engine V2 against the historical crowd observation dataset across
    chronological splits, destinations, and seasons.
    """
    return baseline_evaluation_service.evaluate_baseline()


@router.get("/dataset/quality", response_model=DataQualityReport)
def get_historical_dataset_quality():
    """
    Returns data quality inspection report for the historical crowd dataset,
    auditing missing values, duplicate records, range constraints, and date continuity.
    """
    return data_quality_service.validate_dataset()


@router.get("/forecast-performance/{destination_id}", response_model=ForecastPerformance)
def get_forecast_performance_for_destination(destination_id: str):
    """
    Returns per-destination predictive accuracy for the Forecast Performance card
    in the Command Center right column.
    """
    return forecast_accuracy_engine.get_performance_v2(destination_id=destination_id)




