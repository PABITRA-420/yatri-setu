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

from app.services.ml.eligibility_gate import ProductionEligibilityGate

logger = logging.getLogger(__name__)


class MLTrainingService:
    """
    Orchestrates the full ML training pipeline for crowd pressure prediction.
    """

    def __init__(self):
        self._last_training_report: Optional[Dict[str, Any]] = None
        self._eligibility_gate = ProductionEligibilityGate()

    def train(self, dataset_mode: str = "SYNTHETIC") -> Dict[str, Any]:
        """
        Build dataset, evaluate production eligibility, train model, evaluate,
        compare with baseline, and register.

        Args:
            dataset_mode: 'SYNTHETIC' | 'REAL' | 'MIXED'

        Returns:
            Full training report with metrics, comparison, and provenance.
        """
        mode_clean = dataset_mode.upper().strip()
        logger.info(f"MLTrainingService: starting training (dataset_mode={mode_clean})")

        # 1. Build dataset according to requested mode
        if mode_clean == "SYNTHETIC":
            dataset = ml_dataset_builder.build_synthetic_dataset()
        elif mode_clean == "REAL":
            dataset = ml_dataset_builder.build_historical_dataset(target_horizon=1)
            # Evaluate production eligibility gate for real data
            dates = [r.get("date") for r in dataset.features if r.get("date")]
            date_range = {"start": min(dates), "end": max(dates)} if dates else None
            verdict = self._eligibility_gate.evaluate(
                features=dataset.features,
                targets=dataset.targets,
                destinations=dataset.destinations,
                dataset_mode="REAL",
                date_range=date_range,
            )
            if not verdict.is_eligible:
                logger.warning(f"Production eligibility check failed: {verdict.failure_reasons}")
                report = {
                    "status": "INSUFFICIENT_DATA",
                    "message": (
                        "Insufficient genuine historical data to train a production-grade model. "
                        f"Failed requirements: {'; '.join(verdict.failure_reasons)}"
                    ),
                    "dataset_mode": "REAL",
                    "production_eligible": False,
                    "ml_eligible": False,
                    "eligibility_verdict": verdict.to_dict(),
                    "total_records": dataset.total_records,
                    "destinations": dataset.destinations,
                    "notes": dataset.notes,
                }
                self._last_training_report = report
                return report
        elif mode_clean == "MIXED":
            dataset = ml_dataset_builder.build_mixed_dataset(target_horizon=1)
        else:
            return {
                "error": (
                    f"Dataset mode '{dataset_mode}' is not valid. "
                    "Supported modes are 'REAL', 'SYNTHETIC', and 'MIXED'."
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
            "model_status": getattr(xgboost_crowd_model, "model_status", "UNKNOWN"),
            "production_eligible": getattr(xgboost_crowd_model, "production_eligible", False),
            "feature_schema_version": getattr(xgboost_crowd_model, "feature_schema_version", "2.0.0"),
            "ml_metrics": {
                "val_mae": training_result.get("val_mae"),
                "val_rmse": training_result.get("val_rmse"),
                "test_mae": ml_mae,
                "test_rmse": ml_rmse,
                "test_r2": training_result.get("test_r2"),
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
            "error_by_horizon": training_result.get("error_by_horizon", {}),
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
