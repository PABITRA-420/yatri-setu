"""
XGBoost Crowd Pressure Model with Scikit-Learn Fallback (Milestone 6B).

Implements the BaseCrowdModel contract using a tree-based gradient boosting regressor.
Prediction target: observed_pressure (0–100 normalized crowd pressure score).

Library priority:
  1. XGBoost (xgboost >= 1.7) — preferred for speed and performance
  2. Scikit-Learn GradientBoostingRegressor — safe fallback when XGBoost unavailable

Training constraints:
  - CHRONOLOGICAL SPLITTING ONLY — never random-shuffle time-series data
  - Trained only when build_and_train() is called explicitly
  - Model persisted to disk using joblib for fast inference
  - Never auto-trains on startup to avoid coupling training to the serving path

Data transparency:
  - dataset_mode ('SYNTHETIC' | 'REAL' | 'MIXED') stored in metadata
  - ML model NEVER reports test metrics based solely on synthetic data as production-grade
"""
import os
import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Try XGBoost first, then scikit-learn fallback
_USING_XGBOOST = False
_USING_SKLEARN = False

try:
    import xgboost as xgb
    _USING_XGBOOST = True
    logger.info("XGBoost available — using XGBoostRegressor as primary model.")
except ImportError:
    try:
        from sklearn.ensemble import GradientBoostingRegressor as _GBR
        _USING_SKLEARN = True
        logger.info("XGBoost not available — using scikit-learn GradientBoostingRegressor as fallback.")
    except ImportError:
        logger.warning("Neither XGBoost nor scikit-learn is installed. ML model training is disabled.")

try:
    import joblib
    _JOBLIB_AVAILABLE = True
except ImportError:
    _JOBLIB_AVAILABLE = False
    logger.warning("joblib not available — model persistence disabled.")

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    np = None
    _NUMPY_AVAILABLE = False
    logger.warning("numpy not available — ML array operations disabled.")

from app.services.ml.model_registry import BaseCrowdModel
from app.services.ml.evaluation import (
    compute_mae, compute_rmse, compute_directional_accuracy,
    compute_error_by_destination, compute_error_by_season, compare_models,
)


# Default model save path
DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "models", "crowd_xgb_v1.joblib"
)


class XGBoostCrowdModel(BaseCrowdModel):
    """
    Tree-based gradient boosting crowd pressure predictor.

    When XGBoost is available, uses xgb.XGBRegressor.
    When only scikit-learn is available, uses GradientBoostingRegressor.
    When neither is available, the model is in UNAVAILABLE state and
    all predictions fall back to the BaselineRuleModel.

    Feature vector order must match StandardFeatureBuilder.get_feature_names().
    """

    MODEL_VERSION = "0.1.0"
    DATASET_VERSION = "2023-synthetic-v1"

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self._model = None
        self._feature_names: List[str] = []
        self._feature_importances: Dict[str, float] = {}
        self._model_path = model_path
        self._metadata: Dict[str, Any] = {}
        self._is_trained = False
        self._backend = "unavailable"

        if not _NUMPY_AVAILABLE:
            self._backend = "unavailable"
        elif _USING_XGBOOST:
            self._backend = "xgboost"
        elif _USING_SKLEARN:
            self._backend = "sklearn_gbr"

        # Try to load persisted model
        self._try_load()

    @property
    def name(self) -> str:
        return f"xgboost_crowd_v{self.MODEL_VERSION}"

    @property
    def version(self) -> str:
        return self.MODEL_VERSION

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    @property
    def backend(self) -> str:
        return self._backend

    @property
    def feature_importances(self) -> Dict[str, float]:
        return dict(self._feature_importances)

    def predict(self, features: Dict[str, Any]) -> float:
        """
        Predict crowd pressure score from a feature dictionary.
        Returns value in range [0.0, 100.0].
        Falls back to rule-based baseline if model is not trained.
        """
        if not self._is_trained or self._model is None:
            raise RuntimeError("XGBoostCrowdModel is not trained. Use BaselineRuleModel as fallback.")

        try:
            feature_vector = self._dict_to_vector(features)
            x_input = np.array([feature_vector]) if np is not None else [feature_vector]
            pred = float(self._model.predict(x_input)[0])
            return round(max(0.0, min(100.0, pred)), 1)
        except Exception as e:
            raise RuntimeError(f"XGBoostCrowdModel prediction failed: {e}")

    def build_and_train(
        self,
        feature_rows: List[Dict[str, Any]],
        targets: List[float],
        feature_names: List[str],
        train_indices: List[int],
        validation_indices: List[int],
        test_indices: List[int],
        dataset_mode: str = "SYNTHETIC",
        test_observations=None,
    ) -> Dict[str, Any]:
        """
        Train the gradient boosting model on chronologically split data.

        Args:
            feature_rows: Full list of feature dicts
            targets: Full list of target pressure values
            feature_names: Ordered list of feature column names
            train_indices: Indices into feature_rows for training
            validation_indices: Indices for validation (early stopping)
            test_indices: Indices for final test evaluation
            dataset_mode: 'SYNTHETIC' | 'REAL' | 'MIXED'
            test_observations: Optional list of HistoricalObservation for
                               destination/season breakdown (test split only)

        Returns:
            Full training report with metrics.
        """
        if not _NUMPY_AVAILABLE or np is None:
            return {"error": "numpy is required for ML model training"}

        if self._backend == "unavailable":
            return {"error": "No ML library available (xgboost or scikit-learn required)"}

        self._feature_names = feature_names

        # Build numpy arrays
        X = np.array([[row.get(f, 0.0) for f in feature_names] for row in feature_rows])
        y = np.array(targets)

        X_train, y_train = X[train_indices], y[train_indices]
        X_val, y_val = X[validation_indices], y[validation_indices]
        X_test, y_test = X[test_indices], y[test_indices]

        logger.info(
            f"Training {self._backend} on {len(X_train)} rows "
            f"(val={len(X_val)}, test={len(X_test)}), "
            f"dataset_mode={dataset_mode}"
        )

        # Train model
        if _USING_XGBOOST:
            self._model = xgb.XGBRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                verbosity=0,
            )
            eval_set = [(X_val, y_val)]
            self._model.fit(
                X_train, y_train,
                eval_set=eval_set,
                verbose=False,
            )
            raw_importances = self._model.feature_importances_
        else:
            from sklearn.ensemble import GradientBoostingRegressor
            self._model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42,
            )
            self._model.fit(X_train, y_train)
            raw_importances = self._model.feature_importances_

        # Feature importances
        importance_pairs = sorted(
            zip(feature_names, raw_importances.tolist()),
            key=lambda x: x[1],
            reverse=True,
        )
        self._feature_importances = {name: round(float(imp), 6) for name, imp in importance_pairs}

        # Evaluate on test set
        test_preds = self._model.predict(X_test).tolist()
        test_actuals = y_test.tolist()
        val_preds = self._model.predict(X_val).tolist()

        test_mae = compute_mae(test_preds, test_actuals)
        test_rmse = compute_rmse(test_preds, test_actuals)
        test_dir_acc = compute_directional_accuracy(test_preds, test_actuals)
        val_mae = compute_mae(val_preds, y_val.tolist())
        val_rmse = compute_rmse(val_preds, y_val.tolist())

        # Per-destination/season breakdown (if test observations provided)
        error_by_dest = []
        error_by_season = []
        if test_observations:
            error_by_dest = compute_error_by_destination(test_observations, test_preds)
            error_by_season = compute_error_by_season(test_observations, test_preds)

        # Save metadata
        self._metadata = {
            "model_name": self.name,
            "version": self.MODEL_VERSION,
            "backend": self._backend,
            "dataset_mode": dataset_mode,
            "dataset_version": self.DATASET_VERSION,
            "training_date": datetime.now(timezone.utc).isoformat(),
            "feature_names": feature_names,
            "train_size": len(X_train),
            "validation_size": len(X_val),
            "test_size": len(X_test),
            "val_mae": val_mae,
            "val_rmse": val_rmse,
            "test_mae": test_mae,
            "test_rmse": test_rmse,
            "test_directional_accuracy": test_dir_acc,
            "feature_importances": self._feature_importances,
            "error_by_destination": error_by_dest,
            "error_by_season": error_by_season,
            "synthetic_data_warning": (
                "TRAINED ON SYNTHETIC DATA — Do not report these metrics as production-grade. "
                "Retrain with REAL data before deploying in a live environment."
                if dataset_mode == "SYNTHETIC" else None
            ),
        }

        self._is_trained = True
        self._save()

        return self._metadata

    def get_metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    def _dict_to_vector(self, features: Dict[str, Any]) -> List[float]:
        return [float(features.get(f, 0.0)) for f in self._feature_names]

    def _save(self) -> None:
        if not _JOBLIB_AVAILABLE:
            logger.warning("joblib not available — skipping model persistence.")
            return
        try:
            os.makedirs(os.path.dirname(self._model_path), exist_ok=True)
            payload = {
                "model": self._model,
                "feature_names": self._feature_names,
                "feature_importances": self._feature_importances,
                "metadata": self._metadata,
            }
            joblib.dump(payload, self._model_path)
            logger.info(f"ML model saved to {self._model_path}")
        except Exception as e:
            logger.error(f"Failed to save ML model: {e}")

    def _try_load(self) -> None:
        if not _NUMPY_AVAILABLE or not _JOBLIB_AVAILABLE or not os.path.exists(self._model_path):
            return
        try:
            payload = joblib.load(self._model_path)
            self._model = payload["model"]
            self._feature_names = payload["feature_names"]
            self._feature_importances = payload["feature_importances"]
            self._metadata = payload["metadata"]
            self._is_trained = True
            logger.info(f"ML model loaded from {self._model_path}")
        except Exception as e:
            logger.warning(f"Failed to load persisted ML model ({e}). Model will be in untrained state.")


# Module-level singleton
xgboost_crowd_model = XGBoostCrowdModel()
