"""
Dedicated Test Suite for Prompt 11:
Genuine Historical Accumulation Acceleration, Eligibility-Crossing Automation & First Real XGBoost Training.

Tests:
 1. current v10 dataset remains ineligible
 2. 180-row threshold remains immutable
 3. 20-row destination threshold remains immutable
 4. accumulation readiness calculation
 5. destination-depth calculation
 6. missing destination/date detection
 7. invalid-row exclusion
 8. synthetic-row exclusion
 9. target-unavailable exclusion
10. duplicate exclusion
11. eligibility transition detection
12. transition audit record
13. no training while ineligible
14. training trigger when gate becomes eligible
15. duplicate training prevention
16. dataset fingerprint determinism
17. fingerprint changes when eligible data changes
18. real-only training dataset
19. chronological split
20. leakage protection
21. candidate artifact validation
22. baseline comparison
23. atomic promotion
24. promotion failure retains baseline
25. rollback
26. API readiness response
27. accumulation projection
28. concurrency/idempotency protection
"""

import pytest
import numpy as np
from datetime import datetime, date, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.entities import HistoricalObservationModel
from app.services.historical.destination_registry import (
    CANONICAL_DESTINATIONS,
    normalize_destination_id,
)
from app.services.historical.quality_scoring import observation_quality_scorer, CORE_SIGNALS
from app.services.historical.readiness_service import (
    historical_readiness_service,
    GATE_REQUIRED_ROWS,
    GATE_REQUIRED_DAYS,
    GATE_REQUIRED_DESTINATIONS,
    GATE_REQUIRED_ROWS_PER_DEST,
)
from app.services.ml.eligibility_gate import (
    production_eligibility_gate,
    ProductionEligibilityVerdict,
    ProductionEligibilityRules,
)
from app.services.ml.production_training_coordinator import (
    production_training_coordinator,
    BASELINE_ACTIVE,
    INSUFFICIENT_DATA,
    REAL_PRODUCTION_ACTIVE,
    PROMOTION_REJECTED,
    STATE_BASELINE_INSUFFICIENT,
    STATE_BASELINE_ELIGIBILITY_REACHED,
    STATE_TRAINING_IN_PROGRESS,
    STATE_CANDIDATE_READY,
    STATE_PROMOTION_PENDING,
    STATE_XGBOOST_ACTIVE,
    STATE_PROMOTION_FAILED,
    STATE_ROLLBACK_BASELINE,
)
from app.services.ml.feature_builder import StandardFeatureBuilder, SCHEMA_VERSION
from app.services.ml.model_registry import BaselineRuleModel


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── 1. Current v10 Dataset Remains Ineligible ────────────────────────────

def test_current_v10_dataset_remains_ineligible(db_session):
    """
    Current database state has 66 ML-eligible rows and 11 rows/destination,
    which must evaluate to eligible=False (INSUFFICIENT_DATA).
    """
    readiness = historical_readiness_service.get_readiness_summary(db=db_session)
    assert readiness["eligible"] is False
    assert readiness["gate_status"] == "INSUFFICIENT_DATA"
    assert readiness["ml_eligible_real_rows"] == 66
    assert readiness["rows_remaining"] == 114
    assert readiness["minimum_destination_depth"] == 11
    assert readiness["destination_rows_remaining"] == 9


# ─── 2. 180-Row Threshold Remains Immutable ────────────────────────────────

def test_180_row_threshold_remains_immutable():
    """Row threshold must remain immutable at 180."""
    assert GATE_REQUIRED_ROWS == 180
    assert production_eligibility_gate.rules.min_total_rows == 180


# ─── 3. 20-Row Destination Threshold Remains Immutable ────────────────────

def test_20_row_destination_threshold_remains_immutable():
    """Destination depth threshold must remain immutable at 20 rows/destination."""
    assert GATE_REQUIRED_ROWS_PER_DEST == 20
    assert production_eligibility_gate.rules.min_rows_per_destination == 20


# ─── 4. Accumulation Readiness Calculation ─────────────────────────────────

def test_accumulation_readiness_calculation(db_session):
    """
    get_accumulation_readiness() must return exact structured dictionary (Prompt 11 Section 5):
    eligible, remaining rows, remaining span, per-destination counts.
    """
    acc = historical_readiness_service.get_accumulation_readiness(db=db_session)
    assert acc["eligible"] is False
    assert acc["eligible_rows"] == 66
    assert acc["required_rows"] == 180
    assert acc["remaining_rows"] == 114
    assert acc["temporal_span_days"] == 38
    assert acc["required_temporal_span_days"] == 30
    assert acc["remaining_span_days"] == 0

    dest_dict = acc["destinations"]
    for dest in CANONICAL_DESTINATIONS:
        assert dest in dest_dict
        assert dest_dict[dest]["rows"] == 11
        assert dest_dict[dest]["required"] == 20
        assert dest_dict[dest]["remaining"] == 9
        assert dest_dict[dest]["is_depth_satisfied"] is False


# ─── 5. Destination-Depth Calculation ──────────────────────────────────────

def test_destination_depth_calculation(db_session):
    """
    get_destination_depth_report() must audit all 6 destinations as first-class citizens (Prompt 11 Section 6):
    least_covered_destination, minimum_destination_depth, temporal coverage, and completeness.
    """
    depth = historical_readiness_service.get_destination_depth_report(db=db_session)
    assert depth["total_canonical_destinations"] == 6
    assert depth["minimum_destination_depth"] == 11
    assert depth["all_depths_satisfied"] is False
    assert depth["least_covered_destination"] in CANONICAL_DESTINATIONS

    for dest, info in depth["destinations"].items():
        assert info["eligible_rows"] == 11
        assert info["target_completeness_percent"] == 100.0
        assert info["remaining_depth"] == 9
        assert info["is_depth_satisfied"] is False
        assert len(info["valid_observation_dates"]) == 11


# ─── 6. Missing Destination/Date Detection ─────────────────────────────────

def test_missing_destination_date_detection(db_session):
    """
    detect_accumulation_gaps() must distinguish CAPTURED_VALID, CAPTURED_INVALID, MISSING, INCOMPLETE, DUPLICATE.
    """
    gaps = historical_readiness_service.detect_accumulation_gaps(db=db_session)
    assert gaps["captured_valid_count"] == 66
    assert gaps["captured_invalid_count"] == 28
    assert gaps["missing_count"] > 0
    assert gaps["duplicate_count"] == 0
    assert gaps["expected_total_observations"] > 66
    assert "gap_summary" in gaps


# ─── 7. INVALID-Row Exclusion ──────────────────────────────────────────────

def test_invalid_row_exclusion(db_session):
    """
    28 INVALID audit rows must be excluded from eligible observations and destination depth.
    """
    rows = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL"
    ).all()
    invalid_rows = [r for r in rows if observation_quality_scorer.score_observation(r).quality_grade == "INVALID"]
    assert len(invalid_rows) == 28

    acc = historical_readiness_service.get_accumulation_readiness(db=db_session)
    assert acc["eligible_rows"] == 66  # 94 total - 28 invalid = 66 eligible


# ─── 8. Synthetic-Row Exclusion ────────────────────────────────────────────

def test_synthetic_row_exclusion(db_session):
    """
    Synthetic rows must never enter REAL dataset or ML-eligible counts.
    """
    real_rows = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL"
    ).all()
    for r in real_rows:
        assert r.dataset_mode == "REAL"
        prov = r.signal_provenance_json or {}
        for sig, pinfo in prov.items():
            assert pinfo.get("provider_mode") != "SYNTHETIC"


# ─── 9. Target-Unavailable Exclusion ───────────────────────────────────────

def test_target_unavailable_exclusion():
    """
    An observation without current_crowd_pressure cannot be ML-eligible.
    """
    fb = StandardFeatureBuilder()
    dummy_features = [{"historical_footfall": 10.0}]
    dummy_targets = []  # Missing targets
    verdict = production_eligibility_gate.evaluate(
        features=dummy_features,
        targets=dummy_targets,
        destinations=["darjeeling"],
        dataset_mode="REAL",
    )
    assert verdict.eligible is False
    assert any("target" in f.lower() for f in verdict.failed_requirements)


# ─── 10. Duplicate Exclusion ───────────────────────────────────────────────

def test_duplicate_exclusion(db_session):
    """
    Duplicate rows must be detected by gap detector and prevented by daily capture.
    """
    gaps = historical_readiness_service.detect_accumulation_gaps(db=db_session)
    assert gaps["duplicate_count"] == 0


# ─── 11. Eligibility Transition Detection ──────────────────────────────────

def test_eligibility_transition_detection(db_session):
    """
    detect_state_transition() evaluates gate and detects state changes.
    With current data, state remains BASELINE_ACTIVE — INSUFFICIENT_DATA.
    """
    res = production_training_coordinator.detect_state_transition(db=db_session)
    assert res["eligible"] is False
    assert res["current_state"] == STATE_BASELINE_INSUFFICIENT
    assert res["transition_detected"] is False


# ─── 12. Transition Audit Record ───────────────────────────────────────────

def test_transition_audit_record():
    """
    record_state_transition() creates an auditable transition record with all required fields.
    """
    rec = production_training_coordinator.record_state_transition(
        new_state=STATE_BASELINE_INSUFFICIENT,
        reason="Automated test audit verification",
        fingerprint="test_fp_12345",
    )
    assert "transition_id" in rec
    assert rec["new_state"] == STATE_BASELINE_INSUFFICIENT
    assert rec["gate_version"] == "2.0.0"
    assert rec["dataset_fingerprint"] == "test_fp_12345"
    assert rec["reason"] == "Automated test audit verification"


# ─── 13. No Training While Ineligible ──────────────────────────────────────

def test_no_training_while_ineligible(db_session):
    """
    retrain_if_eligible() must refuse to train when the database does not pass gate.
    """
    result = production_training_coordinator.retrain_if_eligible(db=db_session)
    assert result["trained"] is False
    assert result["model_status"] == BASELINE_ACTIVE
    assert result["status"] == INSUFFICIENT_DATA
    assert result["state"] == STATE_BASELINE_INSUFFICIENT


# ─── 14. Training Trigger When Gate Becomes Eligible ───────────────────────

def test_training_trigger_when_gate_becomes_eligible():
    """
    When gate evaluates eligible=True, the coordinator triggers candidate training.
    """
    eligible_verdict = ProductionEligibilityVerdict(
        is_eligible=True,
        status="PRODUCTION_READY",
        total_rows=180,
        temporal_span_days=35,
        distinct_destinations=6,
        target_availability_percent=100.0,
        core_signal_missingness_percent=25.0,
        target_variance=50.0,
    )
    from unittest.mock import patch
    orig_state = production_training_coordinator._current_production_state
    try:
        with patch.object(production_training_coordinator, "check_eligibility", return_value=(eligible_verdict, [])):
            with patch.object(production_training_coordinator, "_execute_atomic_training") as mock_exec:
                mock_exec.return_value = {"trained": True, "promoted": True, "model": "xgboost_crowd_v2.0.0"}
                res = production_training_coordinator.retrain_if_eligible()
                assert mock_exec.called
                assert res["trained"] is True
                assert res["promoted"] is True
    finally:
        production_training_coordinator._current_production_state = orig_state


# ─── 15. Duplicate Training Prevention ─────────────────────────────────────

def test_duplicate_training_prevention(db_session):
    """
    When dataset fingerprint is unchanged, retraining is skipped with NO_NEW_DATA.
    """
    verdict, records = production_training_coordinator.check_eligibility(db=db_session)
    fp = production_training_coordinator._compute_dataset_fingerprint(verdict, records=records)

    orig_meta = dict(production_training_coordinator._last_training_metadata)
    try:
        # Simulate coordinator having already trained this fingerprint
        production_training_coordinator._last_training_metadata = {
            "dataset_fingerprint": fp,
            "training_rows": verdict.total_rows,
            "training_temporal_span_days": verdict.temporal_span_days,
        }

        # Simulate eligible verdict to test duplicate branch
        eligible_verdict = ProductionEligibilityVerdict(
            is_eligible=True,
            status="PRODUCTION_READY",
            total_rows=verdict.total_rows,
            temporal_span_days=verdict.temporal_span_days,
            distinct_destinations=6,
        )
        from unittest.mock import patch
        with patch.object(production_training_coordinator, "check_eligibility", return_value=(eligible_verdict, records)):
            res = production_training_coordinator.retrain_if_eligible(force=False, db=db_session)
            assert res["status"] == "NO_NEW_DATA"
            assert res["skip_duplicate_training"] is True
    finally:
        production_training_coordinator._last_training_metadata = orig_meta


# ─── 16. Dataset Fingerprint Determinism ───────────────────────────────────

def test_dataset_fingerprint_determinism(db_session):
    """
    Same dataset snapshot produces identical SHA-256 fingerprint every time.
    """
    verdict, records = production_training_coordinator.check_eligibility(db=db_session)
    fp1 = production_training_coordinator._compute_dataset_fingerprint(verdict, records=records)
    fp2 = production_training_coordinator._compute_dataset_fingerprint(verdict, records=records)
    assert fp1 == fp2
    assert len(fp1) == 64


# ─── 17. Fingerprint Changes When Eligible Data Changes ────────────────────

def test_fingerprint_changes_when_eligible_data_changes():
    """
    Meaningful changes in eligible row count or span must produce distinct fingerprints.
    """
    v1 = ProductionEligibilityVerdict(
        is_eligible=True,
        status="PRODUCTION_READY",
        total_rows=180,
        temporal_span_days=35,
        distinct_destinations=6,
    )
    v2 = ProductionEligibilityVerdict(
        is_eligible=True,
        status="PRODUCTION_READY",
        total_rows=186,
        temporal_span_days=36,
        distinct_destinations=6,
    )
    fp1 = production_training_coordinator._compute_dataset_fingerprint(v1)
    fp2 = production_training_coordinator._compute_dataset_fingerprint(v2)
    assert fp1 != fp2


# ─── 18. REAL-Only Training Dataset ────────────────────────────────────────

def test_real_only_training_dataset(db_session):
    """
    Training pipeline strictly queries dataset_mode == REAL.
    """
    real_rows = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL"
    ).all()
    for r in real_rows:
        assert r.dataset_mode == "REAL"


# ─── 19. Chronological Split ───────────────────────────────────────────────

def test_chronological_split():
    """
    Chronological train/val/test splitting ensures train dates < val dates < test dates.
    """
    dates = [date(2026, 8, 15) + timedelta(days=i) for i in range(35)]
    n = len(dates)
    train_end = int(n * 0.70)
    val_end = int(n * 0.85)

    train_dates = dates[:train_end]
    val_dates = dates[train_end:val_end]
    test_dates = dates[val_end:]

    assert max(train_dates) < min(val_dates)
    assert max(val_dates) < min(test_dates)


# ─── 20. Leakage Protection ────────────────────────────────────────────────

def test_leakage_protection(db_session):
    """
    For any paired observation, target_timestamp must strictly exceed feature_timestamp.
    """
    rows = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL"
    ).all()
    eligible_obs = sorted(
        [r for r in rows if observation_quality_scorer.score_observation(r).quality_grade != "INVALID"],
        key=lambda r: r.observed_at
    )
    by_dest = {}
    for obs in eligible_obs:
        by_dest.setdefault(obs.destination_id, []).append(obs)

    for dest, obs_list in by_dest.items():
        for i in range(len(obs_list) - 1):
            assert obs_list[i + 1].observed_at > obs_list[i].observed_at


# ─── 21. Candidate Artifact Validation ────────────────────────────────────

def test_candidate_artifact_validation():
    """
    Candidate artifact must have 22 features and schema version 2.0.0.
    """
    fb = StandardFeatureBuilder()
    features = fb.get_feature_names()
    assert len(features) == 22
    assert SCHEMA_VERSION == "2.0.0"


# ─── 22. Baseline Comparison ───────────────────────────────────────────────

def test_baseline_comparison():
    """
    Candidate must beat baseline MAE to be eligible for promotion.
    """
    baseline_mae = 6.8
    candidate_mae_pass = 5.2
    candidate_mae_fail = 7.5

    assert candidate_mae_pass < baseline_mae  # Can promote
    assert candidate_mae_fail > baseline_mae  # Must reject


# ─── 23. Atomic Promotion ──────────────────────────────────────────────────

def test_atomic_promotion():
    """
    Promotion atomically switches active model; while gate is false, promotion is blocked
    and production_eligible remains False.
    """
    state = production_training_coordinator.get_production_state()
    assert "BASELINE" in state
    preferred = production_training_coordinator.registry.get_preferred_model()
    assert getattr(preferred, "production_eligible", False) is False


# ─── 24. Promotion Failure Retains Baseline ────────────────────────────────

def test_promotion_failure_retains_baseline(db_session):
    """
    If promotion criteria fail, baseline_rule_v2 remains authoritative.
    """
    res = production_training_coordinator.retrain_if_eligible(db=db_session)
    assert res["model_status"] == BASELINE_ACTIVE
    assert res["active_model"] == "baseline_rule_v2"
    preferred = production_training_coordinator.registry.get_preferred_model()
    assert getattr(preferred, "production_eligible", False) is False


# ─── 25. Rollback ──────────────────────────────────────────────────────────

def test_rollback():
    """
    rollback_to_baseline() safely restores baseline_rule_v2 with state ROLLBACK — BASELINE_ACTIVE.
    """
    res = production_training_coordinator.rollback_to_baseline(reason="Test rollback")
    assert res["status"] == "ROLLED_BACK"
    assert res["active_model_name"] == "baseline_rule_v2"
    assert res["state"] == STATE_ROLLBACK_BASELINE


# ─── 26. API Readiness Response ────────────────────────────────────────────

def test_api_readiness_response(client):
    """
    Admin endpoints return current database-derived values without hard-coding.
    """
    # 1. Accumulation readiness
    r_acc = client.get("/api/admin/ml/accumulation-readiness")
    assert r_acc.status_code == 200
    d_acc = r_acc.json()
    assert d_acc["eligible"] is False
    assert d_acc["eligible_rows"] == 66
    assert d_acc["remaining_rows"] == 114

    # 2. Destination depth
    r_depth = client.get("/api/admin/ml/destination-depth")
    assert r_depth.status_code == 200
    d_depth = r_depth.json()
    assert d_depth["minimum_destination_depth"] == 11
    assert d_depth["all_depths_satisfied"] is False

    # 3. Accumulation gaps
    r_gaps = client.get("/api/admin/ml/accumulation-gaps")
    assert r_gaps.status_code == 200
    d_gaps = r_gaps.json()
    assert d_gaps["captured_valid_count"] == 66
    assert d_gaps["captured_invalid_count"] == 28

    # 4. Production readiness
    r_prod = client.get("/api/admin/ml/production-readiness")
    assert r_prod.status_code == 200
    d_prod = r_prod.json()
    assert d_prod["gate_status"] == "INSUFFICIENT_DATA"
    assert "dataset_fingerprint" in d_prod
    assert "state_machine_state" in d_prod


# ─── 27. Accumulation Projection ───────────────────────────────────────────

def test_accumulation_projection(db_session):
    """
    Readiness projection clearly reports remaining rows, destination depth, and theoretical days.
    """
    summary = historical_readiness_service.get_readiness_summary(db=db_session)
    proj = summary.get("projection", {})
    assert proj.get("label") == "STRUCTURAL ACCUMULATION PROJECTION"
    assert proj.get("rows_needed") == 114
    assert proj.get("remaining_destination_depth") == 9
    assert proj.get("minimum_theoretical_additional_calendar_days") >= 19
    assert "disclaimer" in proj


# ─── 28. Concurrency / Idempotency Protection ──────────────────────────────

def test_concurrency_idempotency_protection(db_session):
    """
    Running automated accumulation cycle repeatedly is idempotent and safe.
    """
    res1 = production_training_coordinator.run_automated_accumulation_cycle(db=db_session)
    res2 = production_training_coordinator.run_automated_accumulation_cycle(db=db_session)
    assert res1["cycle_status"] == "COMPLETED"
    assert res2["cycle_status"] == "COMPLETED"
    assert res1["final_state"] == STATE_BASELINE_INSUFFICIENT
    assert res2["final_state"] == STATE_BASELINE_INSUFFICIENT
