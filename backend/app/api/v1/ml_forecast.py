"""
ML-Aware Forecast API (Milestone 6B).

Extends the existing pressure forecast endpoint to support multi-horizon predictions
(1, 3, 7, 14 days) with ML model output where available, and transparent fallback
to the deterministic BaselineRuleModel when ML is not trained.

Confidence disclaimers:
  - Confidence scores are heuristic estimates, NOT statistically calibrated.
  - They are clearly labeled as 'heuristic' in all responses.
  - Confidence degrades with forecast horizon (more uncertainty for longer windows).
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.ml.model_registry import model_registry
from app.services.ml.feature_builder import StandardFeatureBuilder
from app.services.crowd_engine_v2 import crowd_engine_v2

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/destinations", tags=["ML Forecast"])

_feature_builder = StandardFeatureBuilder()

# Heuristic confidence decay by horizon (NOT statistically calibrated)
HORIZON_CONFIDENCE = {
    1:  0.88,
    3:  0.78,
    7:  0.65,
    14: 0.50,
}

VALID_HORIZONS = [1, 3, 7, 14]


class MLForecastDay(BaseModel):
    date: str
    day_name: str
    predicted_pressure: float = Field(ge=0.0, le=100.0)
    pressure_level: str
    model_used: str
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_note: str = "Heuristic estimate — not statistically calibrated"
    fallback_reason: Optional[str] = None
    is_weekend: bool = False


class MLForecastResponse(BaseModel):
    destination_id: str
    destination_name: str
    horizon_days: int
    current_pressure: float
    forecast: List[MLForecastDay]
    model_used: str
    model_version: str
    dataset_mode: Optional[str] = None
    fallback_active: bool
    confidence_note: str = (
        "Confidence values are heuristic estimates that decay with forecast horizon. "
        "They have NOT been statistically calibrated against held-out data."
    )
    generated_at: str


def _pressure_level(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MODERATE"
    return "LOW"


@router.get("/{destination_id}/pressure/forecast/ml", response_model=MLForecastResponse)
def get_ml_pressure_forecast(
    destination_id: str,
    days: int = Query(7, description="Forecast horizon: 1, 3, 7, or 14 days", ge=1, le=14),
):
    """
    Multi-horizon crowd pressure forecast using the trained ML model (if available).

    - Uses XGBoostCrowdModel if trained, with automatic fallback to BaselineRuleModel.
    - Supports 1, 3, 7, and 14-day horizons.
    - Confidence values are heuristic (NOT statistically calibrated).
    - Fallback is transparent: 'fallback_active' and 'fallback_reason' are always returned.
    """
    dest = destination_id.lower().strip()

    # Use existing crowd engine for current pressure reference
    try:
        current = crowd_engine_v2.calculate_pressure(dest, None)
        current_pressure = current.pressure_score
        dest_name = current.destination_name
    except Exception:
        current_pressure = 50.0
        dest_name = dest.title()

    # Use the crowd engine's 7-day forecast as base signal inputs
    try:
        base_forecast = crowd_engine_v2.calculate_pressure_forecast(dest, max(days, 7))
        base_days = base_forecast.forecast_days
    except Exception:
        base_days = []

    forecast_days: List[MLForecastDay] = []
    fallback_active = False
    model_used_name = "baseline_rule_v2"
    model_version = "2.0.0"
    dataset_mode = None

    for d in range(days):
        target_date = (datetime.now(timezone.utc) + timedelta(days=d + 1)).date()
        date_str = target_date.strftime("%Y-%m-%d")
        day_name = target_date.strftime("%A")
        is_weekend = target_date.weekday() >= 4

        # Build feature dict from the base forecast if available
        if d < len(base_days):
            base = base_days[d]
            features = {
                "historical_footfall": current_pressure,
                "accommodation_occupancy": current_pressure * 0.95,
                "booking_demand": current_pressure * 0.9,
                "search_demand": current_pressure * 1.05,
                "event_pressure": float(getattr(base, "is_holiday", False)) * 50.0 + 15.0,
                "holiday_pressure": float(getattr(base, "is_holiday", False)) * 60.0,
                "weather_pressure": 55.0,
                "traffic_pressure": current_pressure * 0.85,
                "day_of_week": target_date.weekday(),
                "is_weekend": int(is_weekend),
                "month": target_date.month,
                "day_of_year": target_date.timetuple().tm_yday,
                "search_to_booking_ratio": 1.05,
                "is_peak_summer": int(target_date.month in (4, 5, 6)),
                "is_peak_autumn": int(target_date.month in (9, 10, 11)),
                **{f"dest_{d_}": int(d_ == dest) for d_ in ["darjeeling","kalimpong","mirik","lava","lolegaon","rishop"]},
            }
        else:
            features = {
                "historical_footfall": current_pressure,
                "accommodation_occupancy": current_pressure * 0.95,
                "booking_demand": current_pressure * 0.9,
                "search_demand": current_pressure * 1.05,
                "event_pressure": 20.0,
                "holiday_pressure": 15.0,
                "weather_pressure": 55.0,
                "traffic_pressure": current_pressure * 0.85,
                "day_of_week": target_date.weekday(),
                "is_weekend": int(is_weekend),
                "month": target_date.month,
                "day_of_year": target_date.timetuple().tm_yday,
                "search_to_booking_ratio": 1.0,
                "is_peak_summer": int(target_date.month in (4, 5, 6)),
                "is_peak_autumn": int(target_date.month in (9, 10, 11)),
                **{f"dest_{d_}": int(d_ == dest) for d_ in ["darjeeling","kalimpong","mirik","lava","lolegaon","rishop"]},
            }

        # Use ML-aware safe_predict (with automatic fallback)
        result = model_registry.safe_predict(features)
        predicted = result["predicted_pressure"]
        m_used = result["model_used"]
        fallback_reason = result.get("fallback_reason")

        if fallback_reason:
            fallback_active = True
        else:
            model_used_name = m_used

        # Heuristic confidence decay: further horizon = lower confidence
        closest_horizon = min(VALID_HORIZONS, key=lambda h: abs(h - (d + 1)))
        confidence = HORIZON_CONFIDENCE.get(closest_horizon, 0.50)

        forecast_days.append(MLForecastDay(
            date=date_str,
            day_name=day_name,
            predicted_pressure=predicted,
            pressure_level=_pressure_level(predicted),
            model_used=m_used,
            confidence=confidence,
            fallback_reason=fallback_reason,
            is_weekend=is_weekend,
        ))

    # Get metadata if ML model trained
    meta = model_registry.get_preferred_model()
    if hasattr(meta, "_metadata") and meta._metadata:
        dataset_mode = meta._metadata.get("dataset_mode")
        model_version = getattr(meta, "version", "2.0.0")

    return MLForecastResponse(
        destination_id=dest,
        destination_name=dest_name,
        horizon_days=days,
        current_pressure=current_pressure,
        forecast=forecast_days,
        model_used=model_used_name,
        model_version=model_version,
        dataset_mode=dataset_mode,
        fallback_active=fallback_active,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
