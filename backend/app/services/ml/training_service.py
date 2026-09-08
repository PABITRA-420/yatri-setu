"""
ML Training Service (Milestone 6B).

Orchestrates end-to-end ML model training:
  1. Builds ML dataset from the available historical data
  2. Runs chronological splitting (TRAIN / VALIDATION / TEST)
  3. Trains XGBoostCrowdModel (or sklearn fallback)
  4. Evaluates against test set
  5. Compares with baseline
  6. Registers the trained model in ModelRegistry

This service is the single entry point for triggering ML training.
It is called explicitly (never on startup) to avoid coupling training to serving.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from app.services.ml.dataset_builder import ml_dataset_builder
from app.services.ml.xgboost_model import xgboost_crowd_model
from app.services.ml.model_registry import model_registry, BaselineRuleModel
from app.services.ml.evaluation import (
    compute_mae, compute_rmse, compute_directional_accuracy,
    compare_models,
)

logger = logging.getLogger(__name__)


class MLTrainingService:
    """
    Orchestrates the full ML training pipeline for crowd pressure prediction.
    """

    def __init__(self):
        self._last_training_report: Optional[Dict[str, Any]] = None

    def train(self, dataset_mode: str = "SYNTHETIC") -> Dict[str, Any]:
        """
        Build dataset, train model, evaluate, compare with baseline, and register.

        Args:
            dataset_mode: 'SYNTHETIC' | 'REAL' | 'MIXED'
                          Currently only SYNTHETIC is supported.

        Returns:
            Full training report with metrics, comparison, and provenance.
        """
        logger.info(f"MLTrainingService: starting training (dataset_mode={dataset_mode})")

        # 1. Build dataset
        if dataset_mode == "SYNTHETIC":
            dataset = ml_dataset_builder.build_synthetic_dataset()
        else:
            return {
                "error": (
                    f"Dataset mode '{dataset_mode}' is not yet supported. "
                    "Only SYNTHETIC is available until real ingestors accumulate data."
                )
            }

        split = dataset.split
        feature_rows = dataset.features
        targets = dataset.targets
        feature_names = dataset.feature_names

        train_idx = split["train_indices"]
        val_idx = split["validation_indices"]
        test_idx = split["test_indices"]

        test_obs = split["test"]

        # 2. Train XGBoost
        training_result = xgboost_crowd_model.build_and_train(
            feature_rows=feature_rows,
            targets=targets,
            feature_names=feature_names,
            train_indices=train_idx,
            validation_indices=val_idx,
            test_indices=test_idx,
            dataset_mode=dataset_mode,
            test_observations=test_obs,
        )

        if "error" in training_result:
            return training_result

        # 3. Register the trained model (overwrite previous if exists)
        model_registry.register_model(xgboost_crowd_model)

        # 4. Compute baseline on test set for honest comparison
        baseline = BaselineRuleModel()
        test_features = [feature_rows[i] for i in test_idx]
        baseline_preds = [baseline.predict(f) for f in test_features]
        test_actuals = [targets[i] for i in test_idx]

        baseline_mae = compute_mae(baseline_preds, test_actuals)
        baseline_rmse = compute_rmse(baseline_preds, test_actuals)
        baseline_dir_acc = compute_directional_accuracy(baseline_preds, test_actuals)

        ml_mae = training_result.get("test_mae", 0.0)
        ml_rmse = training_result.get("test_rmse", 0.0)
        ml_dir_acc = training_result.get("test_directional_accuracy", 0.0)

        comparison = compare_models(baseline_mae, ml_mae, baseline_rmse, ml_rmse)

        report = {
            "status": "SUCCESS",
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "model_name": xgboost_crowd_model.name,
            "model_version": xgboost_crowd_model.version,
            "backend": xgboost_crowd_model.backend,
            "dataset_mode": dataset_mode,
            "dataset_summary": ml_dataset_builder.get_dataset_summary(dataset),
            "split_sizes": {
                "train": len(train_idx),
                "validation": len(val_idx),
                "test": len(test_idx),
            },
            "split_dates": {
                "train": {"start": split["train_start"], "end": split["train_end"]},
                "validation": {"start": split["val_start"], "end": split["val_end"]},
                "test": {"start": split["test_start"], "end": split["test_end"]},
            },
            "ml_metrics": {
                "val_mae": training_result.get("val_mae"),
                "val_rmse": training_result.get("val_rmse"),
                "test_mae": ml_mae,
                "test_rmse": ml_rmse,
                "test_directional_accuracy": ml_dir_acc,
            },
            "baseline_metrics": {
                "test_mae": baseline_mae,
                "test_rmse": baseline_rmse,
                "test_directional_accuracy": baseline_dir_acc,
            },
            "comparison": comparison,
            "feature_importances": xgboost_crowd_model.feature_importances,
            "error_by_destination": training_result.get("error_by_destination", []),
            "error_by_season": training_result.get("error_by_season", []),
            "synthetic_data_warning": training_result.get("synthetic_data_warning"),
        }

        self._last_training_report = report
        logger.info(
            f"MLTrainingService: training complete. "
            f"ML MAE={ml_mae:.3f}, Baseline MAE={baseline_mae:.3f}, "
            f"Improves={comparison['ml_improves_over_baseline']}"
        )
        return report

    def get_last_report(self) -> Optional[Dict[str, Any]]:
        return self._last_training_report


ml_training_service = MLTrainingService()
