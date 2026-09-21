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
    model_status: Optional[str] = None
    production_eligible: bool = False
    feature_schema_version: Optional[str] = "2.0.0"
    feature_timestamp: Optional[str] = None
    forecast_source_classification: Optional[str] = Field(
        None,
        description="REAL_XGBOOST_FORECAST | SYNTHETIC_BENCHMARK | BASELINE_FALLBACK | INSUFFICIENT_DATA"
    )


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
    - Feature vectors are constructed using canonical StandardFeatureBuilder.
    - Confidence values are heuristic (NOT statistically calibrated).
    - Fallback is transparent: 'fallback_active' and 'fallback_reason' are always returned.
    """
    dest = destination_id.lower().strip()

    # Use canonical Crowd Engine V2 for current pressure reference
    try:
        current = crowd_engine_v2.calculate_pressure(dest, None)
        current_pressure = current.pressure_score
        dest_name = current.destination_name
    except Exception:
        current_pressure = 50.0
        dest_name = dest.title()
        current = None

    # Base forecast for calendar/holiday context
    try:
        base_forecast = crowd_engine_v2.calculate_pressure_forecast(dest, max(days, 7))
        base_days = base_forecast.forecast_days
    except Exception:
        base_days = []

    now_dt = datetime.now(timezone.utc)
    feature_date = now_dt.date()
    feature_timestamp_str = feature_date.strftime("%Y-%m-%d")

    # Extract genuine available signals from Crowd Engine V2 (no artificial multipliers)
    current_telemetry: Dict[str, Any] = {}
    if current and hasattr(current, "signals") and current.signals:
        for s in current.signals:
            if getattr(s, "available", True):
                val = getattr(s, "value", None)
                if val is not None:
                    k = getattr(s, "signal_key", "")
                    if k in ("footfall", "historical_footfall"):
                        current_telemetry["footfall"] = val
                    elif k in ("accommodation", "accommodation_occupancy"):
                        current_telemetry["accommodation_occupancy"] = val
                    elif k in ("booking", "booking_demand"):
                        current_telemetry["booking_demand"] = val
                    elif k in ("search", "search_demand"):
                        current_telemetry["search_demand"] = val
                    elif k in ("events", "event_pressure"):
                        current_telemetry["event_pressure"] = val
                    elif k in ("holidays", "holiday_pressure"):
                        current_telemetry["holiday_pressure"] = val
                    elif k in ("weather", "weather_pressure"):
                        current_telemetry["weather_pressure"] = val
                    elif k in ("traffic", "traffic_pressure"):
                        current_telemetry["traffic_pressure"] = val

    # Fallback to current composite pressure if footfall was not separately measured
    if "footfall" not in current_telemetry:
        current_telemetry["footfall"] = current_pressure

    forecast_days: List[MLForecastDay] = []
    fallback_active = False
    model_used_name = "baseline_rule_v2"
    model_version = "2.0.0"
    dataset_mode = None
    model_status = None
    production_eligible = False
    feature_schema_version = "2.0.0"

    preferred = model_registry.get_preferred_model()
    if preferred:
        model_used_name = preferred.name
        model_version = preferred.version
        model_status = getattr(preferred, "model_status", "BASELINE" if "baseline" in preferred.name else "UNKNOWN")
        production_eligible = getattr(preferred, "production_eligible", False)
        if hasattr(preferred, "_metadata") and preferred._metadata:
            dataset_mode = preferred._metadata.get("dataset_mode", getattr(preferred, "dataset_mode", None))
            feature_schema_version = preferred._metadata.get("feature_schema_version", "2.0.0")

    for d in range(days):
        target_horizon_days = d + 1
        target_date = feature_date + timedelta(days=target_horizon_days)
        date_str = target_date.strftime("%Y-%m-%d")
        day_name = target_date.strftime("%A")
        is_weekend = target_date.weekday() >= 4

        # Contextual day signals (e.g. from calendar/base forecast)
        day_telemetry = dict(current_telemetry)
        if d < len(base_days):
            base = base_days[d]
            is_hol = getattr(base, "is_holiday", False)
            if is_hol:
                day_telemetry["holiday_pressure"] = 60.0
                day_telemetry["event_pressure"] = max(day_telemetry.get("event_pressure", 20.0), 50.0)

        # Single Source of Truth: Canonical StandardFeatureBuilder
        features = _feature_builder.build_inference_features(
            destination_id=dest,
            target_date=target_date,
            feature_date=feature_date,
            target_horizon_days=target_horizon_days,
            horizon_days=target_horizon_days,
            current_telemetry=day_telemetry
        )

        # Safe prediction with schema validation & baseline fallback
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

    # Determine explicit classification distinguishing REAL vs SYNTHETIC vs BASELINE vs INSUFFICIENT
    if fallback_active or "baseline" in model_used_name:
        if fallback_reason and "insufficient" in fallback_reason.lower():
            classification = "INSUFFICIENT_DATA"
        else:
            classification = "BASELINE_FALLBACK"
    elif dataset_mode == "REAL" and production_eligible:
        classification = "REAL_XGBOOST_FORECAST"
    elif dataset_mode == "SYNTHETIC":
        classification = "SYNTHETIC_BENCHMARK"
    else:
        classification = "BASELINE_FALLBACK"

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
        confidence_note=(
            "Confidence values are heuristic estimates that decay with forecast horizon. "
            "They have NOT been statistically calibrated against held-out data."
        ),
        generated_at=now_dt.isoformat(),
        model_status=model_status,
        production_eligible=production_eligible,
        feature_schema_version=feature_schema_version,
        feature_timestamp=feature_timestamp_str,
        forecast_source_classification=classification,
    )
