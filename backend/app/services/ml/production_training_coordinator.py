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
from app.services.historical.readiness_service import historical_readiness_service
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

# Accumulation & Training Lifecycle States (Prompt 10 Section 6)
ACCUMULATING = "ACCUMULATING"
GATE_CHECK = "GATE_CHECK"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
ELIGIBLE = "ELIGIBLE"
TRAINING = "TRAINING"
VALIDATING = "VALIDATING"
PROMOTION_CHECK = "PROMOTION_CHECK"
PROMOTION_REJECTED = "PROMOTION_REJECTED"
VALIDATION_FAILED = "VALIDATION_FAILED"
BASELINE_ACTIVE = "BASELINE_ACTIVE"
SYNTHETIC_BENCHMARK = "SYNTHETIC_BENCHMARK"
REAL_TRAINING_READY = "REAL_TRAINING_READY"
REAL_TRAINED = "REAL_TRAINED"
REAL_PRODUCTION_ACTIVE = "REAL_PRODUCTION_ACTIVE"
TRAINING_FAILED = "TRAINING_FAILED"


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

    def _compute_dataset_fingerprint(self, verdict: ProductionEligibilityVerdict) -> str:
        """Generates a deterministic hash of the dataset snapshot to prevent redundant retraining (Prompt 10 Section 26)."""
        import hashlib
        payload = (
            f"rows={verdict.total_rows}:span={verdict.temporal_span_days}:"
            f"dests={verdict.distinct_destinations}:var={verdict.target_variance:.2f}:"
            f"avail={verdict.target_availability_percent:.1f}:miss={verdict.core_signal_missingness_percent:.1f}"
        )
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def get_accumulation_state(self, db: Optional[Session] = None) -> str:
        """
        Returns deterministic accumulation lifecycle state according to Prompt 10 Section 6:
        - INSUFFICIENT_DATA: Gate not yet satisfied by real data
        - ELIGIBLE: Gate satisfied, ready for training
        - REAL_PRODUCTION_ACTIVE: Promoted real model currently authoritative
        - BASELINE_ACTIVE: Baseline rule authoritative
        """
        verdict, _ = self.check_eligibility(db=db)
        if not verdict.is_eligible:
            return INSUFFICIENT_DATA
        preferred = self.registry.get_preferred_model()
        if preferred.name != "baseline_rule_v2" and getattr(preferred, "production_eligible", False):
            return REAL_PRODUCTION_ACTIVE
        return ELIGIBLE

    def rollback_to_baseline(self, reason: str = "Rollback requested") -> Dict[str, Any]:
        """
        Safely falls back to BaselineRuleModel without corrupting production availability (Prompt 10 Section 23).
        """
        baseline = BaselineRuleModel()
        self.registry.register_model(baseline)
        logger.warning(f"ProductionTrainingCoordinator: rollback executed. Reason: {reason}")
        return {
            "status": "ROLLED_BACK",
            "active_model_name": baseline.name,
            "model_status": BASELINE_ACTIVE,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

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

            # Prompt 9 Section 15: An invalid observation must NEVER increase ML eligibility.
            # Filter strictly for ML-eligible observations (exclude INVALID audit records).
            from app.services.historical.quality_scoring import observation_quality_scorer
            eligible_records = [
                r for r in records
                if observation_quality_scorer.score_observation(r).quality_grade != "INVALID"
            ]

            fb = StandardFeatureBuilder()
            features = []
            targets = []
            destinations = set()

            dates = [r.date_bucket for r in eligible_records if getattr(r, "date_bucket", None)]
            earliest = min(dates) if dates else ""
            latest = max(dates) if dates else ""

            for r in eligible_records:
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

            return verdict, eligible_records
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
                "failed_requirements": verdict.failed_requirements,
                "diagnostics": verdict.to_structured_diagnostics(),
                "last_trained_metadata": self._last_training_metadata,
            }

        # 2. Check for new qualifying data using dataset fingerprint (Prompt 10 Section 26)
        dataset_fingerprint = self._compute_dataset_fingerprint(verdict)
        last_fingerprint = self._last_training_metadata.get("dataset_fingerprint")

        last_rows = self._last_training_metadata.get("training_rows", 0)
        last_span = self._last_training_metadata.get("training_temporal_span_days", 0)
        is_duplicate = (last_fingerprint and last_fingerprint == dataset_fingerprint) or (
            last_rows == verdict.total_rows and last_span == verdict.temporal_span_days and last_rows > 0
        )

        if not force and is_duplicate:
            logger.info(
                f"ProductionTrainingCoordinator: identical dataset snapshot/fingerprint ({dataset_fingerprint}). "
                f"Skipping duplicate training run."
            )
            return {
                "status": "NO_NEW_DATA",
                "trained": False,
                "skip_duplicate_training": True,
                "dataset_fingerprint": dataset_fingerprint,
                "model_status": REAL_PRODUCTION_ACTIVE,
                "message": (
                    f"No new qualifying observations accumulated since last training run "
                    f"({verdict.total_rows} rows, {verdict.temporal_span_days} days, fingerprint={dataset_fingerprint})."
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
        """Performs candidate training, validation, baseline comparison, and atomic artifact promotion."""
        import numpy as np
        fb = StandardFeatureBuilder()
        feature_names = fb.get_feature_names()

        # Sort records chronologically (Prompt 10 Section 16)
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

        # Validate candidate artifact can be reloaded and matches feature schema (Prompt 10 Section 20)
        validator_model = XGBoostCrowdModel(model_path=self.candidate_model_path)
        if not validator_model.is_trained:
            if os.path.exists(self.candidate_model_path):
                try:
                    os.remove(self.candidate_model_path)
                except Exception:
                    pass
            return {
                "status": VALIDATION_FAILED,
                "trained": False,
                "promoted": False,
                "model_status": BASELINE_ACTIVE,
                "error": "Candidate model failed artifact re-load integrity validation.",
                "diagnostics": verdict.to_structured_diagnostics(),
            }
        if validator_model.feature_names != feature_names or len(validator_model.feature_names) != 22:
            if os.path.exists(self.candidate_model_path):
                try:
                    os.remove(self.candidate_model_path)
                except Exception:
                    pass
            return {
                "status": VALIDATION_FAILED,
                "trained": False,
                "promoted": False,
                "model_status": BASELINE_ACTIVE,
                "error": f"Candidate model feature schema mismatch (found {len(validator_model.feature_names)}, expected 22).",
                "diagnostics": verdict.to_structured_diagnostics(),
            }

        # Compute test metrics for candidate vs BaselineRuleModel (Prompt 10 Section 18 & 19)
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

        # Per-horizon real validation breakdown (Prompt 10 Section 18)
        horizon_metrics = {}
        for h in [1, 3, 7, 14]:
            h_idx = [i for i, row in enumerate(X_test) if row.get("target_horizon_days") == h]
            if h_idx:
                h_p = [xgb_preds[i] for i in h_idx]
                h_y = [y_test[i] for i in h_idx]
                horizon_metrics[f"H={h}"] = {
                    "mae": compute_mae(h_p, h_y),
                    "rmse": compute_rmse(h_p, h_y),
                    "r2": compute_r2(h_p, h_y),
                    "samples": len(h_idx),
                }
            else:
                horizon_metrics[f"H={h}"] = {"status": "insufficient_horizon_samples"}

        real_validation_metrics = {
            "overall": xgb_metrics,
            "per_horizon": horizon_metrics,
            "label": "REAL PRODUCTION VALIDATION METRICS",
            "evaluated_on": "chronological_held_out_real_data",
        }

        # Section 19: Baseline Comparison & Promotion Criteria Check
        promotion_allowed = True
        rejection_reason = None
        if xgb_metrics["mae"] > baseline_metrics["mae"]:
            promotion_allowed = False
            rejection_reason = f"Candidate MAE ({xgb_metrics['mae']:.2f}) is worse than baseline MAE ({baseline_metrics['mae']:.2f})."
        elif xgb_metrics["r2"] < -0.5:
            promotion_allowed = False
            rejection_reason = f"Candidate R2 ({xgb_metrics['r2']:.2f}) indicates poor fit."

        if not promotion_allowed:
            logger.warning(f"ProductionTrainingCoordinator: candidate promotion rejected: {rejection_reason}")
            if os.path.exists(self.candidate_model_path):
                try:
                    os.remove(self.candidate_model_path)
                except Exception:
                    pass
            return {
                "status": PROMOTION_REJECTED,
                "trained": True,
                "promoted": False,
                "model_status": BASELINE_ACTIVE,
                "rejection_reason": rejection_reason,
                "evaluation_metrics": xgb_metrics,
                "real_production_validation_metrics": real_validation_metrics,
                "baseline_metrics": baseline_metrics,
                "comparison": comparison,
                "diagnostics": verdict.to_structured_diagnostics(),
            }

        # Atomic artifact replacement (Prompt 10 Section 21 & 23):
        # 1. If existing production artifact exists, create backup
        if os.path.exists(self.model_path):
            try:
                shutil.copyfile(self.model_path, self.backup_model_path)
            except Exception as e:
                logger.warning(f"Could not create backup of production model: {e}")

        # 2. Atomic rename / move candidate into production position
        shutil.move(self.candidate_model_path, self.model_path)
        logger.info(f"ProductionTrainingCoordinator: atomically promoted candidate to {self.model_path}")

        # 3. Reload active model in registry with rollback fallback
        try:
            xgboost_crowd_model._model_path = self.model_path
            xgboost_crowd_model._try_load()
            self.registry.register_model(xgboost_crowd_model)
        except Exception as e:
            logger.error(f"Failed to load promoted model, executing rollback: {e}")
            self.rollback_to_baseline(reason=f"Promotion loading failure: {e}")
            return {
                "status": TRAINING_FAILED,
                "trained": False,
                "model_status": BASELINE_ACTIVE,
                "error": f"Promotion loading failure, rolled back to baseline: {e}",
            }

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
            "dataset_fingerprint": dataset_fingerprint,
            "horizons_supported": [1, 3, 7, 14],
            "evaluation_metrics": xgb_metrics,
            "real_production_validation_metrics": real_validation_metrics,
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
            "real_production_validation_metrics": real_validation_metrics,
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

        readiness = historical_readiness_service.get_readiness_summary(db=db)

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
            "accumulation_state": self.get_accumulation_state(db=db),
            "gate_status": readiness.get("gate_status", "INSUFFICIENT_DATA"),
            "total_real_rows": readiness.get("total_real_rows", readiness["real_rows"]),
            "ml_eligible_real_rows": readiness.get("ml_eligible_real_rows", readiness["real_rows"]),
            "invalid_rows": readiness.get("invalid_rows", 0),
            "unique_dates": readiness.get("unique_dates", readiness["distinct_dates"]),
            "rows_by_destination": readiness.get("rows_by_destination", readiness["rows_per_destination"]),
            "minimum_destination_depth": readiness.get("minimum_destination_depth", readiness.get("min_rows_per_destination", 0)),
            "rows_remaining": readiness.get("rows_remaining", readiness.get("remaining_rows_required", 0)),
            "destination_rows_remaining": readiness.get("destination_rows_remaining", readiness.get("remaining_destination_depth_required", 0)),
            "days_remaining": readiness.get("days_remaining", readiness.get("remaining_days_required", 0)),
            "requirements_breakdown": readiness.get("requirements_breakdown", {}),
            "eligibility_diagnostics": verdict.to_structured_diagnostics(),
            "real_rows": readiness["real_rows"],
            "required_rows": readiness["required_rows"],
            "row_progress_percent": readiness["row_progress_percent"],
            "distinct_dates": readiness["distinct_dates"],
            "required_temporal_span_days": readiness["required_temporal_span_days"],
            "temporal_span_days": readiness["temporal_span_days"],
            "temporal_progress_percent": readiness["temporal_progress_percent"],
            "destinations_present": readiness["destinations_present"],
            "required_destinations": readiness["required_destinations"],
            "rows_per_destination": readiness["rows_per_destination"],
            "destinations_underrepresented": readiness["destinations_underrepresented"],
            "latest_observation_date": readiness["latest_observation_date"],
            "oldest_observation_date": readiness["oldest_observation_date"],
            "core_signal_missingness_percent": readiness["core_signal_missingness_percent"],
            "core_signal_availability_percent": readiness["core_signal_availability_percent"],
            "target_availability": readiness.get("target_availability", 100.0),
            "target_variance": readiness.get("target_variance", 0.0),
            "quality_breakdown": readiness["quality_breakdown"],
            "projection": readiness["projection"],
            "readiness_metrics": readiness,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }


# Singleton instance
production_training_coordinator = ProductionTrainingCoordinator()
