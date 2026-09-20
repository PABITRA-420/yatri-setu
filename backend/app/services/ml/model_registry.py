"""
Model Registry & Inference Interfaces for Crowd Intelligence (Milestone 6A/6B).

Registers, inspects, and retrieves crowd pressure models.
Supports both the deterministic BaselineRuleModel (always available) and
tree-based ML models (XGBoost/Sklearn GBR) that require explicit training.

Fallback guarantee:
  If the active model raises any exception during predict(),
  the registry ALWAYS falls back to BaselineRuleModel.
  No user-facing API should ever crash because ML is unavailable.
"""
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BaseCrowdModel(ABC):
    """Abstract contract for crowd pressure predictive models."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> float:
        """Generate a predicted crowd pressure score (0.0 to 100.0)."""

    def batch_predict(self, features_list: List[Dict[str, Any]]) -> List[float]:
        """Generate predictions for a sequence of feature dictionaries."""
        return [self.predict(f) for f in features_list]


class BaselineRuleModel(BaseCrowdModel):
    """
    Deterministic rule-based Crowd Engine V2 packaged under the BaseCrowdModel contract.
    Serves as the benchmark against which all ML models are evaluated.
    Always available — no training required.
    """

    WEIGHTS = {
        "historical_footfall": 0.15,
        "accommodation_occupancy": 0.15,
        "booking_demand": 0.15,
        "search_demand": 0.10,
        "event_pressure": 0.10,
        "holiday_pressure": 0.10,
        "weather_pressure": 0.10,
        "traffic_pressure": 0.15,
    }

    @property
    def name(self) -> str:
        return "baseline_rule_v2"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def model_status(self) -> str:
        return "BASELINE"

    @property
    def production_eligible(self) -> bool:
        return True

    def predict(self, features: Dict[str, Any]) -> float:
        """
        Predict crowd pressure using weighted rule formula.
        Dynamically renormalizes over available non-null, non-NaN signals
        to avoid converting missing telemetry into artificial zeros or defaults.
        """
        valid_items = []
        for sig, weight in self.WEIGHTS.items():
            val = features.get(sig)
            if val is not None:
                try:
                    fval = float(val)
                    if fval == fval:  # not NaN
                        valid_items.append((fval, weight))
                except (ValueError, TypeError):
                    pass

        if valid_items:
            total_weight = sum(w for _, w in valid_items)
            score = sum(val * w for val, w in valid_items) / total_weight
        else:
            score = 50.0

        return round(max(0.0, min(100.0, score)), 1)


class ModelRegistry:
    """
    Central repository for registering, inspecting, and retrieving crowd models.

    Fallback contract:
      Every predict() call is wrapped in a try/except.
      If the preferred model fails or schema does not match, BaselineRuleModel is used automatically.
      This guarantees no user-facing endpoint crashes due to ML unavailability.
    """

    def __init__(self):
        self._baseline = BaselineRuleModel()
        self._models: Dict[str, BaseCrowdModel] = {}
        self.register_model(self._baseline)
        self.auto_register_persisted_models()

    def register_model(self, model: BaseCrowdModel) -> None:
        self._models[model.name] = model
        logger.info(f"ModelRegistry: registered model '{model.name}' v{model.version}")

    def get_model(self, name: str) -> Optional[BaseCrowdModel]:
        return self._models.get(name)

    def auto_register_persisted_models(self) -> None:
        """
        Auto-register persisted XGBoost model from disk if it was previously trained
        and passes feature schema integrity checks.
        """
        try:
            from app.services.ml.xgboost_model import xgboost_crowd_model
            if getattr(xgboost_crowd_model, "is_trained", False):
                self.register_model(xgboost_crowd_model)
                logger.info("ModelRegistry: successfully auto-registered persisted XGBoost model from disk.")
        except Exception as e:
            logger.warning(f"ModelRegistry: auto-registration of persisted model skipped: {e}")

    def get_preferred_model(self) -> BaseCrowdModel:
        """
        Return the best available trained ML model.
        Falls back to the deterministic baseline if no ML model is trained.
        """
        for model in self._models.values():
            if model.name != "baseline_rule_v2":
                if getattr(model, "is_trained", False):
                    return model
        return self._baseline

    def safe_predict(self, features: Dict[str, Any], prefer_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Safely predict crowd pressure with automatic fallback to baseline.

        Returns a dict with:
          - predicted_pressure: float
          - model_used: str
          - model_version: str
          - model_status: str
          - production_eligible: bool
          - dataset_mode: str
          - feature_schema_version: str
          - feature_importances: dict
          - fallback_active: bool
          - fallback_reason: str | None
        """
        model = self._models.get(prefer_model) if prefer_model else self.get_preferred_model()

        # Try the preferred model first
        if model and model.name != "baseline_rule_v2":
            try:
                pred = model.predict(features)
                return {
                    "predicted_pressure": pred,
                    "model_used": model.name,
                    "model_version": model.version,
                    "model_status": getattr(model, "model_status", "UNKNOWN"),
                    "production_eligible": getattr(model, "production_eligible", False),
                    "dataset_mode": getattr(model, "dataset_mode", "UNKNOWN"),
                    "feature_schema_version": getattr(model, "feature_schema_version", "2.0.0"),
                    "feature_importances": getattr(model, "feature_importances", {}),
                    "fallback_active": False,
                    "fallback_reason": None,
                }
            except Exception as e:
                logger.warning(
                    f"ML model '{model.name}' prediction failed ({e}). "
                    f"Falling back to BaselineRuleModel."
                )
                fallback_reason = f"ML model prediction error ({type(e).__name__}): {e}"
        else:
            fallback_reason = "No trained ML model available; using deterministic baseline."

        # Baseline fallback (always succeeds)
        pred = self._baseline.predict(features)
        return {
            "predicted_pressure": pred,
            "model_used": self._baseline.name,
            "model_version": self._baseline.version,
            "model_status": "BASELINE_FALLBACK" if (prefer_model or model != self._baseline) else "BASELINE",
            "production_eligible": False,
            "dataset_mode": "DETERMINISTIC_RULES",
            "feature_schema_version": "2.0.0",
            "feature_importances": {},
            "fallback_active": True if (prefer_model or model != self._baseline) else False,
            "fallback_reason": fallback_reason,
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """List all registered models with their metadata."""
        results = []
        for m in self._models.values():
            entry = {
                "name": m.name,
                "version": m.version,
                "type": "BASELINE_RULE" if "baseline" in m.name else "ML_REGRESSOR",
                "backend": getattr(m, "backend", "rule_based"),
                "is_trained": getattr(m, "is_trained", True),
                "model_status": getattr(m, "model_status", "BASELINE" if "baseline" in m.name else "UNKNOWN"),
                "production_eligible": getattr(m, "production_eligible", False),
                "dataset_mode": getattr(m, "dataset_mode", "REAL" if "baseline" not in m.name else "DETERMINISTIC_RULES"),
            }
            metadata = getattr(m, "_metadata", {})
            if metadata:
                entry["training_date"] = metadata.get("training_date")
                entry["dataset_mode"] = metadata.get("dataset_mode", entry["dataset_mode"])
                entry["dataset_version"] = metadata.get("dataset_version")
                entry["feature_schema_version"] = metadata.get("feature_schema_version", "2.0.0")
                entry["training_rows"] = metadata.get("training_rows")
                entry["destination_count"] = metadata.get("destination_count")
                entry["horizons_supported"] = metadata.get("horizons_supported", [1, 3, 7, 14])
                entry["test_mae"] = metadata.get("test_mae")
                entry["test_rmse"] = metadata.get("test_rmse")
                entry["test_r2"] = metadata.get("test_r2")
                entry["test_directional_accuracy"] = metadata.get("test_directional_accuracy")
                entry["production_eligible"] = metadata.get("production_eligible", False)
                entry["top_features"] = metadata.get("top_features", [])
            results.append(entry)
        return results


# Singleton instance
model_registry = ModelRegistry()
