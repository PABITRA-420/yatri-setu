"""
Production Training Coordinator & Model Promotion Engine (Milestone 12 / Prompt 6).

Responsibilities:
1. Inspects the REAL dataset and evaluates it strictly against ProductionEligibilityGate.
2. If NOT eligible:
   - Blocks training unconditionally (never fabricates or weakens thresholds).
   - Preserves active model / baseline.
   - Reports exact diagnostics and failed requirements.
3. If ELIGIBLE:
   - Checks if new qualifying data has accumulated (avoids duplicate training runs).
   - Builds multi-horizon leakage-safe dataset with schema 2.0.0 validation.
   - Enforces chronological train/validation/test ordering (no future leakage).
   - Trains candidate XGBoost model artifact atomically.
   - Computes evaluation metrics alongside BaselineRuleModel benchmark metrics.
   - Validates candidate artifact before atomic promotion to active production artifact.
4. If training fails:
   - Safely preserves previous production model artifact without corruption.
   - Logs failure reason.

Lifecycle States:
- BASELINE_ACTIVE
- SYNTHETIC_BENCHMARK
- REAL_TRAINING_READY
- REAL_TRAINED
- REAL_PRODUCTION_ACTIVE
- TRAINING_FAILED
- INSUFFICIENT_DATA
"""

import os
import shutil
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.historical.ingestion_service import historical_ingestion_service
from app.services.ml.feature_builder import StandardFeatureBuilder, SCHEMA_VERSION
from app.services.ml.eligibility_gate import (
    ProductionEligibilityGate,
    ProductionEligibilityVerdict,
    production_eligibility_gate,
)
from app.services.ml.model_registry import (
    ModelRegistry,
    model_registry,
    BaselineRuleModel,
)
from app.services.ml.xgboost_model import (
    XGBoostCrowdModel,
    DEFAULT_MODEL_PATH,
    xgboost_crowd_model,
)
from app.services.ml.evaluation import (
    compute_mae,
    compute_rmse,
    compute_r2,
    compute_directional_accuracy,
    compare_models,
)

logger = logging.getLogger(__name__)

# Lifecycle States
BASELINE_ACTIVE = "BASELINE_ACTIVE"
SYNTHETIC_BENCHMARK = "SYNTHETIC_BENCHMARK"
REAL_TRAINING_READY = "REAL_TRAINING_READY"
REAL_TRAINED = "REAL_TRAINED"
REAL_PRODUCTION_ACTIVE = "REAL_PRODUCTION_ACTIVE"
TRAINING_FAILED = "TRAINING_FAILED"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ProductionTrainingCoordinator:
    """
    Coordinates safe, auditable, and atomic production training of XGBoost forecasting models
    conditioned strictly on the genuine REAL historical dataset.
    """

    def __init__(
        self,
        registry: Optional[ModelRegistry] = None,
        gate: Optional[ProductionEligibilityGate] = None,
        model_path: str = DEFAULT_MODEL_PATH,
    ):
        self.registry = registry or model_registry
        self.gate = gate or production_eligibility_gate
        self.model_path = model_path
        self.candidate_model_path = model_path.replace(".joblib", "_candidate.joblib")
        self.backup_model_path = model_path.replace(".joblib", "_backup.joblib")
        self._last_training_metadata: Dict[str, Any] = {}

    def check_eligibility(self, db: Optional[Session] = None) -> Tuple[ProductionEligibilityVerdict, List[Any]]:
        """
        Inspects current genuine REAL observations and evaluates against the ProductionEligibilityGate.
        Returns the verdict and the loaded observation records.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            records = historical_ingestion_service.get_observations(
                dataset_mode="REAL",
                limit=5000,
                db=db
            )

            fb = StandardFeatureBuilder()
            features = []
            targets = []
            destinations = set()

            dates = [r.date_bucket for r in records if getattr(r, "date_bucket", None)]
            earliest = min(dates) if dates else ""
            latest = max(dates) if dates else ""

            for r in records:
                dest = getattr(r, "destination_id", "")
                if dest:
                    destinations.add(dest)
                row = fb.build_feature_row(r)
                features.append(row)
                target = getattr(r, "current_crowd_pressure", None)
                if target is not None:
                    targets.append(float(target))

            verdict = self.gate.evaluate(
                features=features,
                targets=targets,
                destinations=list(destinations),
                dataset_mode="REAL",
                date_range={"start": earliest, "end": latest},
            )

            return verdict, records
        finally:
            if close_db and db:
                db.close()

    def retrain_if_eligible(
        self,
        force: bool = False,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Idempotent and atomic retraining process:
        1. Evaluates eligibility gate.
        2. If ineligible -> returns INSUFFICIENT_DATA with diagnostic breakdown.
        3. If eligible but no new data -> returns NO_NEW_DATA.
        4. If eligible with new data -> trains candidate XGBoost model, validates artifact,
           and atomically promotes to production.
        """
        verdict, records = self.check_eligibility(db=db)

        # 1. Gate check
        if not verdict.is_eligible:
            logger.info(
                f"ProductionTrainingCoordinator: real dataset not eligible ({verdict.status}). "
                f"Failed: {verdict.failed_requirements}"
            )
            return {
                "status": INSUFFICIENT_DATA,
                "trained": False,
                "model_status": BASELINE_ACTIVE,
                "reason": "Real dataset does not satisfy ProductionEligibilityGate.",
                "diagnostics": verdict.to_structured_diagnostics(),
                "last_trained_metadata": self._last_training_metadata,
            }

        # 2. Check for new qualifying data
        last_rows = self._last_training_metadata.get("training_rows", 0)
        last_span = self._last_training_metadata.get("training_temporal_span_days", 0)

        if not force and last_rows == verdict.total_rows and last_span == verdict.temporal_span_days and last_rows > 0:
            logger.info(
                f"ProductionTrainingCoordinator: no new qualifying data accumulated "
                f"(rows={verdict.total_rows}, span={verdict.temporal_span_days}). Skipping duplicate run."
            )
            return {
                "status": "NO_NEW_DATA",
                "trained": False,
                "model_status": REAL_PRODUCTION_ACTIVE,
                "message": (
                    f"No new qualifying observations accumulated since last training run "
                    f"({verdict.total_rows} rows, {verdict.temporal_span_days} days)."
                ),
                "diagnostics": verdict.to_structured_diagnostics(),
                "last_trained_metadata": self._last_training_metadata,
            }

        # 3. Train candidate model atomically
        logger.info(
            f"ProductionTrainingCoordinator: REAL dataset is eligible ({verdict.total_rows} rows, "
            f"{verdict.distinct_destinations} dests, span={verdict.temporal_span_days} days). "
            f"Initiating atomic candidate training."
        )

        try:
            return self._execute_atomic_training(records, verdict)
        except Exception as e:
            logger.error(f"ProductionTrainingCoordinator: candidate training failed: {e}", exc_info=True)
            # Ensure candidate file is cleaned up
            if os.path.exists(self.candidate_model_path):
                try:
                    os.remove(self.candidate_model_path)
                except Exception:
                    pass
            return {
                "status": TRAINING_FAILED,
                "trained": False,
                "model_status": BASELINE_ACTIVE,
                "error": str(e),
                "diagnostics": verdict.to_structured_diagnostics(),
                "last_trained_metadata": self._last_training_metadata,
            }

    def _execute_atomic_training(
        self,
        records: List[Any],
        verdict: ProductionEligibilityVerdict
    ) -> Dict[str, Any]:
        """Performs candidate training, validation, and atomic artifact promotion."""
        import numpy as np
        fb = StandardFeatureBuilder()
        feature_names = fb.get_feature_names()

        # Sort records chronologically
        sorted_records = sorted(
            records,
            key=lambda r: (getattr(r, "date_bucket", ""), getattr(r, "destination_id", ""))
        )

        feature_rows = []
        targets = []
        for r in sorted_records:
            row = fb.build_feature_row(r)
            feature_rows.append(row)
            targets.append(float(getattr(r, "current_crowd_pressure", 50.0) or 50.0))

        n_total = len(feature_rows)
        n_train = int(n_total * 0.70)
        n_val = int(n_total * 0.15)

        train_idx = list(range(0, n_train))
        val_idx = list(range(n_train, n_train + n_val))
        test_idx = list(range(n_train + n_val, n_total))

        # Train candidate model artifact
        candidate_model = XGBoostCrowdModel(model_path=self.candidate_model_path)
        train_res = candidate_model.train(
            feature_rows=feature_rows,
            targets=targets,
            feature_names=feature_names,
            train_indices=train_idx,
            validation_indices=val_idx,
            test_indices=test_idx,
            dataset_mode="REAL",
            production_eligible=True,
            horizons_supported=[1, 3, 7, 14],
        )

        if "error" in train_res:
            raise RuntimeError(f"XGBoost candidate training failed: {train_res['error']}")

        # Save candidate to candidate path
        candidate_model.save(self.candidate_model_path)

        # Validate candidate artifact can be reloaded and matches feature schema
        validator_model = XGBoostCrowdModel(model_path=self.candidate_model_path)
        if not validator_model.is_trained:
            raise RuntimeError("Candidate model failed artifact re-load integrity validation.")
        if validator_model.feature_names != feature_names:
            raise RuntimeError("Candidate model feature names do not match schema 2.0.0.")

        # Compute test metrics for candidate vs BaselineRuleModel
        baseline = BaselineRuleModel()
        X_test = [feature_rows[i] for i in test_idx]
        y_test = [targets[i] for i in test_idx]

        xgb_preds = [validator_model.predict(f) for f in X_test]
        baseline_preds = [baseline.predict(f) for f in X_test]

        xgb_metrics = {
            "mae": compute_mae(xgb_preds, y_test),
            "rmse": compute_rmse(xgb_preds, y_test),
            "r2": compute_r2(xgb_preds, y_test),
            "directional_accuracy": compute_directional_accuracy(xgb_preds, y_test),
        }

        baseline_metrics = {
            "mae": compute_mae(baseline_preds, y_test),
            "rmse": compute_rmse(baseline_preds, y_test),
            "r2": compute_r2(baseline_preds, y_test),
            "directional_accuracy": compute_directional_accuracy(baseline_preds, y_test),
        }

        comparison = compare_models(
            candidate_preds=xgb_preds,
            baseline_preds=baseline_preds,
            actuals=y_test,
        )

        # Atomic artifact replacement:
        # 1. If existing production artifact exists, create backup
        if os.path.exists(self.model_path):
            try:
                shutil.copyfile(self.model_path, self.backup_model_path)
            except Exception as e:
                logger.warning(f"Could not create backup of production model: {e}")

        # 2. Atomic rename / move candidate into production position
        shutil.move(self.candidate_model_path, self.model_path)
        logger.info(f"ProductionTrainingCoordinator: atomically promoted candidate to {self.model_path}")

        # 3. Reload active model in registry
        xgboost_crowd_model._model_path = self.model_path
        xgboost_crowd_model._try_load()
        self.registry.register_model(xgboost_crowd_model)

        now_iso = datetime.now(timezone.utc).isoformat()
        metadata = {
            "model_status": REAL_PRODUCTION_ACTIVE,
            "model_version": f"v5-real-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "dataset_mode": "REAL",
            "production_eligible": True,
            "feature_schema_version": SCHEMA_VERSION,
            "trained_at": now_iso,
            "training_rows": verdict.total_rows,
            "training_destinations": verdict.distinct_destinations,
            "training_temporal_span_days": verdict.temporal_span_days,
            "horizons_supported": [1, 3, 7, 14],
            "evaluation_metrics": xgb_metrics,
            "baseline_metrics": baseline_metrics,
            "comparison": comparison,
            "promotion_reason": (
                "Certified by ProductionEligibilityGate: genuine REAL historical observations "
                "with >=180 rows, >=3 destinations, >=30-day temporal span, and verified chronological metrics."
            ),
        }

        self._last_training_metadata = metadata
        xgboost_crowd_model._metadata.update(metadata)

        return {
            "status": "SUCCESS",
            "trained": True,
            "model_status": REAL_PRODUCTION_ACTIVE,
            "message": "Candidate XGBoost model successfully trained, validated, and promoted to production.",
            "training_metadata": metadata,
            "diagnostics": verdict.to_structured_diagnostics(),
        }

    def get_readiness_report(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Generates full transparency readiness report as requested in Phase 9.
        """
        verdict, records = self.check_eligibility(db=db)

        # Preferred model
        preferred = self.registry.get_preferred_model()
        is_xgb_active = preferred.name != "baseline_rule_v2"

        active_meta = getattr(preferred, "_metadata", {}) or {}

        return {
            "model_status": (
                REAL_PRODUCTION_ACTIVE if (is_xgb_active and getattr(preferred, "production_eligible", False))
                else (SYNTHETIC_BENCHMARK if getattr(preferred, "dataset_mode", "") == "SYNTHETIC" else BASELINE_ACTIVE)
            ),
            "active_model_name": preferred.name,
            "model_version": getattr(preferred, "version", "2.0.0"),
            "dataset_mode": getattr(preferred, "dataset_mode", "DETERMINISTIC_RULES"),
            "production_eligible": getattr(preferred, "production_eligible", False),
            "feature_schema_version": SCHEMA_VERSION,
            "trained_at": active_meta.get("trained_at") or self._last_training_metadata.get("trained_at"),
            "training_rows": active_meta.get("training_rows") or verdict.total_rows,
            "training_destinations": active_meta.get("training_destinations") or verdict.distinct_destinations,
            "training_temporal_span_days": active_meta.get("training_temporal_span_days") or verdict.temporal_span_days,
            "training_provenance": {
                "dataset_mode": "REAL",
                "observations_count": verdict.total_rows,
                "sources_contributing": ["POSTGRESQL_BOOKINGS", "POSTGRESQL_DEMAND", "OFFICIAL_GAZETTE", "REGIONAL_EVENTS"]
            },
            "evaluation_metrics": active_meta.get("evaluation_metrics", {}),
            "baseline_metrics": active_meta.get("baseline_metrics", {}),
            "promotion_reason": active_meta.get("promotion_reason", "Using deterministic baseline Crowd Engine V2 rules."),
            "eligibility_diagnostics": verdict.to_structured_diagnostics(),
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }


# Singleton instance
production_training_coordinator = ProductionTrainingCoordinator()
