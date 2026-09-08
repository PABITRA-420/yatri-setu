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

    def predict(self, features: Dict[str, Any]) -> float:
        score = sum(
            features.get(sig, 50.0) * weight
            for sig, weight in self.WEIGHTS.items()
        )
        return round(max(0.0, min(100.0, score)), 1)


class ModelRegistry:
    """
    Central repository for registering, inspecting, and retrieving crowd models.

    Fallback contract:
      Every predict() call is wrapped in a try/except.
      If the preferred model fails, BaselineRuleModel is used automatically.
      This guarantees no user-facing endpoint crashes due to ML unavailability.
    """

    def __init__(self):
        self._baseline = BaselineRuleModel()
        self._models: Dict[str, BaseCrowdModel] = {}
        self.register_model(self._baseline)

    def register_model(self, model: BaseCrowdModel) -> None:
        self._models[model.name] = model
        logger.info(f"ModelRegistry: registered model '{model.name}' v{model.version}")

    def get_model(self, name: str) -> Optional[BaseCrowdModel]:
        return self._models.get(name)

    def get_preferred_model(self) -> BaseCrowdModel:
        """
        Return the best available trained ML model.
        Falls back to the deterministic baseline if no ML model is trained.
        """
        # Prefer ML models (non-baseline) if they are trained
        for model in self._models.values():
            if model.name != "baseline_rule_v2":
                # Check if it has an is_trained attribute and it's True
                if getattr(model, "is_trained", True):
                    return model
        return self._baseline

    def safe_predict(self, features: Dict[str, Any], prefer_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Safely predict crowd pressure with automatic fallback to baseline.

        Returns a dict with:
          - predicted_pressure: float
          - model_used: str
          - fallback_reason: str | None (set if ML was bypassed)
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
                    "fallback_reason": None,
                }
            except Exception as e:
                logger.warning(
                    f"ML model '{model.name}' prediction failed ({e}). "
                    f"Falling back to BaselineRuleModel."
                )

        # Baseline fallback (always succeeds)
        pred = self._baseline.predict(features)
        return {
            "predicted_pressure": pred,
            "model_used": self._baseline.name,
            "model_version": self._baseline.version,
            "fallback_reason": "ML model unavailable or prediction failed; using deterministic baseline.",
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
            }
            # Include training metadata if present
            metadata = getattr(m, "_metadata", {})
            if metadata:
                entry["training_date"] = metadata.get("training_date")
                entry["dataset_mode"] = metadata.get("dataset_mode")
                entry["dataset_version"] = metadata.get("dataset_version")
                entry["test_mae"] = metadata.get("test_mae")
                entry["test_rmse"] = metadata.get("test_rmse")
                entry["test_directional_accuracy"] = metadata.get("test_directional_accuracy")
            results.append(entry)
        return results


# Singleton instance
model_registry = ModelRegistry()
