"""
XGBoost Crowd Pressure Forecasting Model (Milestone 6B & Milestone 11 / Prompt 4).

Upgraded production-grade tree ensemble forecasting model.
Predicts future continuous crowd pressure scores (0-100) at horizons H in {1, 3, 7, 14} days.

Core guarantees:
1. UNKNOWN != ZERO: Missing numerical telemetry is represented as np.nan,
   allowing XGBoost's native split direction to handle missingness without fabricating zeros.
2. Single feature schema parity: Validates that feature schema version, names, and order
   match StandardFeatureBuilder.
3. Artifact safety: Validates persisted model artifacts on startup without crashing on mismatch.
4. Model status classification: Distinguishes SYNTHETIC_BENCHMARK, HISTORICAL_PRODUCTION_CANDIDATE,
   and PRODUCTION_READY.
5. Explainability: Exposes gain-based feature importances and top predictive signals.
"""

import os
import logging
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

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
from app.services.ml.feature_builder import StandardFeatureBuilder
from app.services.ml.evaluation import (
    compute_mae, compute_rmse, compute_r2, compute_directional_accuracy,
    compute_error_by_destination, compute_error_by_season, compare_models,
)

DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "models", "crowd_xgb_v1.joblib"
)


class XGBoostCrowdModel(BaseCrowdModel):
    """
    Tree-based gradient boosting crowd pressure predictor.
    Predicts future continuous crowd pressure at horizon H using T-time observations.
    """

    MODEL_VERSION = "2.0.0"
    DATASET_VERSION = "v4-canonical-forecasting"

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self._model = None
        self._feature_names: List[str] = StandardFeatureBuilder().get_feature_names()
        self._feature_importances: Dict[str, float] = {}
        self._model_path = model_path
        self._metadata: Dict[str, Any] = {}
        self._is_trained = False
        self._model_status = "UNTRAINED"
        self._production_eligible = False
        self._backend = "unavailable"

        if not _NUMPY_AVAILABLE:
            self._backend = "unavailable"
        elif _USING_XGBOOST:
            self._backend = "xgboost"
        elif _USING_SKLEARN:
            self._backend = "sklearn_gbr"

        # Try to safely load persisted model artifact
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
    def model_status(self) -> str:
        return self._model_status

    @property
    def production_eligible(self) -> bool:
        return self._production_eligible

    @property
    def feature_names(self) -> List[str]:
        return list(self._feature_names)

    @property
    def feature_importances(self) -> Dict[str, float]:
        return dict(self._feature_importances)

    def predict(self, features: Dict[str, Any]) -> float:
        """
        Predict future crowd pressure score from a feature dictionary.
        Returns continuous value constrained to [0.0, 100.0] rounded to 1 decimal place.
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
        production_eligible: bool = False,
        test_observations=None,
        horizons_supported: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Train the gradient boosting model on chronologically partitioned data.
        """
        if not _NUMPY_AVAILABLE or np is None:
            return {"error": "numpy is required for ML model training"}

        if self._backend == "unavailable":
            return {"error": "No ML library available (xgboost or scikit-learn required)"}

        self._feature_names = feature_names

        # Build numpy arrays with strict np.nan preservation (UNKNOWN != ZERO)
        X = np.array([self._dict_to_vector(row) for row in feature_rows])
        y = np.array(targets)

        X_train, y_train = X[train_indices], y[train_indices]
        X_val, y_val = X[validation_indices], y[validation_indices]
        X_test, y_test = X[test_indices], y[test_indices]

        clean_mode = dataset_mode.upper().strip()
        logger.info(
            f"Training {self._backend} on {len(X_train)} rows "
            f"(val={len(X_val)}, test={len(X_test)}), "
            f"dataset_mode={clean_mode}"
        )

        # Train model with explainable, robust hyperparameter configuration
        if _USING_XGBOOST:
            self._model = xgb.XGBRegressor(
                objective="reg:squarederror",
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
            # Extract gain-based feature importances if available
            try:
                booster = self._model.get_booster()
                score_dict = booster.get_score(importance_type="gain")
                total_gain = sum(score_dict.values())
                if total_gain > 0:
                    raw_importances = [score_dict.get(fn, 0.0) / total_gain for fn in feature_names]
                else:
                    raw_importances = self._model.feature_importances_.tolist()
            except Exception:
                raw_importances = self._model.feature_importances_.tolist()
        else:
            from sklearn.ensemble import GradientBoostingRegressor
            # Scikit-learn doesn't support NaN natively; impute median for training fallback
            from sklearn.impute import SimpleImputer
            imputer = SimpleImputer(strategy="median")
            X_train_imp = imputer.fit_transform(X_train)
            X_val_imp = imputer.transform(X_val)
            X_test_imp = imputer.transform(X_test)

            self._model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                subsample=0.8,
                random_state=42,
            )
            self._model.fit(X_train_imp, y_train)
            raw_importances = self._model.feature_importances_.tolist()
            X_test = X_test_imp
            X_val = X_val_imp

        # Feature importances ranking
        importance_pairs = sorted(
            zip(feature_names, raw_importances),
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
        test_r2 = compute_r2(test_preds, test_actuals)
        test_dir_acc = compute_directional_accuracy(test_preds, test_actuals)

        val_mae = compute_mae(val_preds, y_val.tolist())
        val_rmse = compute_rmse(val_preds, y_val.tolist())
        val_r2 = compute_r2(val_preds, y_val.tolist())

        # Error breakdown by horizon
        error_by_horizon = self._compute_error_by_horizon(
            feature_rows=feature_rows,
            indices=test_indices,
            predictions=test_preds,
            actuals=test_actuals,
        )

        # Error breakdown by destination and season
        error_by_dest = []
        error_by_season = []
        if test_observations:
            error_by_dest = compute_error_by_destination(test_observations, test_preds)
            error_by_season = compute_error_by_season(test_observations, test_preds)

        # Model status determination
        if clean_mode == "SYNTHETIC":
            model_status = "SYNTHETIC_BENCHMARK"
            prod_elig = False
        elif clean_mode == "MIXED":
            model_status = "MIXED_BENCHMARK"
            prod_elig = False
        elif production_eligible:
            model_status = "PRODUCTION_READY"
            prod_elig = True
        else:
            model_status = "HISTORICAL_PRODUCTION_CANDIDATE"
            prod_elig = False

        self._model_status = model_status
        self._production_eligible = prod_elig

        # Save metadata
        self._metadata = {
            "model_name": self.name,
            "version": self.MODEL_VERSION,
            "backend": self._backend,
            "dataset_mode": clean_mode,
            "model_status": model_status,
            "production_eligible": prod_elig,
            "dataset_version": self.DATASET_VERSION,
            "feature_schema_version": StandardFeatureBuilder.SCHEMA_VERSION,
            "training_date": datetime.now(timezone.utc).isoformat(),
            "feature_names": feature_names,
            "horizons_supported": horizons_supported or [1, 3, 7, 14],
            "train_size": len(X_train),
            "validation_size": len(X_val),
            "test_size": len(X_test),
            "val_mae": val_mae,
            "val_rmse": val_rmse,
            "val_r2": val_r2,
            "test_mae": test_mae,
            "test_rmse": test_rmse,
            "test_r2": test_r2,
            "test_directional_accuracy": test_dir_acc,
            "feature_importances": self._feature_importances,
            "error_by_horizon": error_by_horizon,
            "error_by_destination": error_by_dest,
            "error_by_season": error_by_season,
            "synthetic_data_warning": (
                "TRAINED ON SYNTHETIC DATA — Do not report these metrics as production-grade. "
                "Retrain with REAL data before deploying in a live environment."
                if clean_mode in ("SYNTHETIC", "MIXED") else None
            ),
        }

        self._is_trained = True
        self._save()

        return self._metadata

    def _compute_error_by_horizon(
        self,
        feature_rows: List[Dict[str, Any]],
        indices: List[int],
        predictions: List[float],
        actuals: List[float],
    ) -> List[Dict[str, Any]]:
        """Calculates distinct MAE and RMSE per horizon (1, 3, 7, 14 days)."""
        horizon_buckets: Dict[int, Dict[str, List[float]]] = {}

        for idx, pred, act in zip(indices, predictions, actuals):
            row = feature_rows[idx]
            h = int(row.get("target_horizon_days", 1))
            if h not in horizon_buckets:
                horizon_buckets[h] = {"preds": [], "actuals": []}
            horizon_buckets[h]["preds"].append(pred)
            horizon_buckets[h]["actuals"].append(act)

        results = []
        for h in sorted(horizon_buckets.keys()):
            p_list = horizon_buckets[h]["preds"]
            a_list = horizon_buckets[h]["actuals"]
            results.append({
                "horizon_days": h,
                "sample_count": len(p_list),
                "mae": compute_mae(p_list, a_list),
                "rmse": compute_rmse(p_list, a_list),
                "r2": compute_r2(p_list, a_list),
            })

        return results

    def get_metadata(self) -> Dict[str, Any]:
        return dict(self._metadata)

    def _dict_to_vector(self, features: Dict[str, Any]) -> List[float]:
        """
        Converts feature dict to vector matching self._feature_names.
        Distinguishes UNKNOWN from ZERO: None / NaN values are stored as np.nan.
        """
        vector: List[float] = []
        nan_val = np.nan if np is not None else float("nan")

        for f in self._feature_names:
            val = features.get(f)
            if val is None:
                vector.append(nan_val)
            elif isinstance(val, (int, float)):
                if math.isnan(val):
                    vector.append(nan_val)
                else:
                    vector.append(float(val))
            else:
                try:
                    vector.append(float(val))
                except (ValueError, TypeError):
                    vector.append(nan_val)

        return vector

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
        """Safely loads persisted model artifact and validates schema compatibility."""
        if not _NUMPY_AVAILABLE or not _JOBLIB_AVAILABLE or not os.path.exists(self._model_path):
            return
        try:
            payload = joblib.load(self._model_path)
            if not isinstance(payload, dict) or "model" not in payload:
                logger.warning("Invalid model artifact structure; holding model in untrained state.")
                return

            loaded_features = payload.get("feature_names", [])
            expected_features = StandardFeatureBuilder().get_feature_names()

            # Schema validation: feature names must match exactly
            if loaded_features != expected_features:
                logger.warning(
                    f"Model artifact schema mismatch: artifact has {len(loaded_features)} features, "
                    f"expected {len(expected_features)}. Holding model in UNTRAINED state until retrained."
                )
                self._is_trained = False
                self._model_status = "SCHEMA_MISMATCH"
                return

            self._model = payload["model"]
            self._feature_names = loaded_features
            self._feature_importances = payload.get("feature_importances", {})
            self._metadata = payload.get("metadata", {})
            self._model_status = self._metadata.get("model_status", "HISTORICAL_PRODUCTION_CANDIDATE")
            self._production_eligible = self._metadata.get("production_eligible", False)
            self._is_trained = True
            logger.info(f"ML model artifact loaded ({self._model_status}) from {self._model_path}")
        except Exception as e:
            logger.warning(f"Failed to load persisted ML model ({e}). Model will be in untrained state.")
            self._is_trained = False
            self._model_status = "LOAD_FAILED"


xgboost_crowd_model = XGBoostCrowdModel()
