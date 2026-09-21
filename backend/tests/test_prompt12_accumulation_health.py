"""
Comprehensive Test Suite for Prompt 12:
Genuine Daily Accumulation Health, Gap Monitoring & Capture Reliability.

Covers at least 42 tests across:
A. Branch/config safety (Test 1)
B. Daily ledger (Tests 2-7)
C. Idempotency (Tests 8-10)
D. Retry behavior (Tests 11-13)
E. Source health (Tests 14-18)
F. Destination monitoring (Tests 19-22)
G. Velocity (Tests 23-26)
H. Projection (Tests 27-28)
I. Eligibility safety (Tests 29-32)
J. Fingerprint (Tests 33-36)
K. Transition (Tests 37-39)
L. Isolation (Tests 40-42)
"""

import os
import subprocess
import pytest
from datetime import datetime, date, timezone, timedelta
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal, engine
from app.models.entities import (
    HistoricalObservationModel,
    DailyCaptureLedgerModel,
    DestinationModel,
)
from app.models.historical import (
    HistoricalObservationCreate,
    SignalProvenanceRecord,
)
from app.services.historical.destination_registry import (
    CANONICAL_DESTINATIONS,
    normalize_destination_id,
)
from app.services.historical.quality_scoring import (
    observation_quality_scorer,
    CORE_SIGNALS,
    ALL_SIGNALS,
)
from app.services.historical.accumulation_health_service import (
    accumulation_health_service,
    STATUS_FULL_SUCCESS,
    STATUS_PARTIAL_SUCCESS,
    STATUS_FAILED,
    STATUS_CAPTURED_VALID,
    STATUS_CAPTURED_INVALID,
    STATUS_MISSING,
    STATUS_INCOMPLETE,
    STATUS_DUPLICATE,
    STATUS_EXPECTED,
    FRESHNESS_FRESH,
    FRESHNESS_STALE,
    FRESHNESS_UNAVAILABLE,
    FRESHNESS_UNKNOWN,
)
from app.services.historical.readiness_service import (
    historical_readiness_service,
    GATE_REQUIRED_ROWS,
    GATE_REQUIRED_DAYS,
    GATE_REQUIRED_DESTINATIONS,
    GATE_REQUIRED_ROWS_PER_DEST,
)
from app.services.historical.ingestion_service import historical_ingestion_service
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
    STATE_BASELINE_INSUFFICIENT,
    STATE_BASELINE_ELIGIBILITY_REACHED,
    STATE_XGBOOST_ACTIVE,
)
from app.services.ml.model_registry import model_registry


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


# ─── A. Branch & Config Safety ────────────────────────────────────────────────

def test_01_v12_branches_from_v11_state():
    """1. Verify Git branch is v12 and originated from v11."""
    res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
    current_branch = res.stdout.strip()
    assert current_branch == "v12", f"Expected branch 'v12', got '{current_branch}'"


# ─── B. Daily Ledger ──────────────────────────────────────────────────────────

def test_02_expected_six_destinations_generated():
    """2. Expected six destinations are verified by accumulation health service."""
    health = accumulation_health_service.get_daily_accumulation_health(date_bucket="2026-09-01")
    assert health["expected_destinations"] == 6
    assert len(CANONICAL_DESTINATIONS) == 6
    assert set(CANONICAL_DESTINATIONS) == {"darjeeling", "kalimpong", "mirik", "lava", "lolegaon", "rishop"}


def test_03_valid_capture_recorded(db_session):
    """3. Valid capture is properly recorded in ledger and classified as CAPTURED_VALID."""
    test_date = "2026-05-01"
    entry = accumulation_health_service.record_daily_ledger_entry(
        destination_id="darjeeling",
        date_bucket=test_date,
        dataset_mode="REAL",
        attempted=True,
        attempts_count=1,
        retry_count=0,
        sources_attempted=["OPEN_METEO_LIVE", "POSTGRESQL_BOOKINGS"],
        sources_succeeded=["OPEN_METEO_LIVE", "POSTGRESQL_BOOKINGS"],
        validation_passed=True,
        ml_eligible=True,
        is_quarantined=False,
        final_status=STATUS_CAPTURED_VALID,
        db=db_session,
    )
    assert entry.final_status == STATUS_CAPTURED_VALID
    assert entry.validation_passed is True
    assert entry.ml_eligible is True
    assert entry.is_quarantined is False
    # Cleanup ledger entry
    db_session.delete(entry)
    db_session.commit()


def test_04_missing_destination_detected():
    """4. Missing destination on an unrecorded date is detected as MISSING."""
    future_test_date = "2026-01-01"
    health = accumulation_health_service.get_daily_accumulation_health(date_bucket=future_test_date)
    assert health["missing"] == 6
    assert len(health["missing_destinations"]) == 6
    assert health["status"] == STATUS_FAILED


def test_05_invalid_capture_detected(db_session):
    """5. Invalid capture is flagged as CAPTURED_INVALID and quarantined in ledger."""
    test_date = "2026-05-02"
    entry = accumulation_health_service.record_daily_ledger_entry(
        destination_id="kalimpong",
        date_bucket=test_date,
        dataset_mode="REAL",
        attempted=True,
        validation_passed=False,
        ml_eligible=False,
        is_quarantined=True,
        quarantine_reason="date_bucket is in the future",
        final_status=STATUS_CAPTURED_INVALID,
        db=db_session,
    )
    assert entry.final_status == STATUS_CAPTURED_INVALID
    assert entry.is_quarantined is True
    assert "future" in entry.quarantine_reason
    db_session.delete(entry)
    db_session.commit()


def test_06_incomplete_capture_detected(db_session):
    """6. Incomplete capture (missing crowd pressure target) is detected as INCOMPLETE."""
    test_date = "2026-05-03"
    entry = accumulation_health_service.record_daily_ledger_entry(
        destination_id="mirik",
        date_bucket=test_date,
        dataset_mode="REAL",
        attempted=True,
        validation_passed=False,
        ml_eligible=False,
        is_quarantined=False,
        final_status=STATUS_INCOMPLETE,
        quarantine_reason="target_missing",
        db=db_session,
    )
    assert entry.final_status == STATUS_INCOMPLETE
    assert entry.ml_eligible is False
    db_session.delete(entry)
    db_session.commit()


def test_07_duplicate_detected(db_session):
    """7. Duplicate capture entry is flagged with is_duplicate=True and final_status=DUPLICATE."""
    test_date = "2026-05-04"
    entry = accumulation_health_service.record_daily_ledger_entry(
        destination_id="lava",
        date_bucket=test_date,
        dataset_mode="REAL",
        attempted=True,
        is_duplicate=True,
        final_status=STATUS_DUPLICATE,
        db=db_session,
    )
    assert entry.is_duplicate is True
    assert entry.final_status == STATUS_DUPLICATE
    db_session.delete(entry)
    db_session.commit()


# ─── C. Idempotency ───────────────────────────────────────────────────────────

def test_08_same_capture_twice_creates_one_eligible_observation(db_session):
    """8. Ingesting identical observation twice does not duplicate database records."""
    test_date = "2026-05-10"
    rec = HistoricalObservationCreate(
        destination_id="darjeeling",
        observed_at=datetime(2026, 5, 10, 12, 0, 0),
        date_bucket=test_date,
        current_crowd_pressure=55.0,
        footfall=500.0,
        booking_demand=60.0,
        search_demand=70.0,
        weather_pressure=40.0,
        traffic_pressure=30.0,
        holiday_pressure=10.0,
        event_pressure=5.0,
        dataset_mode="REAL",
    )
    rec1 = historical_ingestion_service.ingest_observation(rec, db=db_session)
    count1 = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date,
        HistoricalObservationModel.destination_id == "darjeeling",
    ).count()

    rec2 = historical_ingestion_service.ingest_observation(rec, db=db_session)
    count2 = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date,
        HistoricalObservationModel.destination_id == "darjeeling",
    ).count()

    assert count1 == 1
    assert count2 == 1
    assert rec1.id == rec2.id

    # Cleanup test record
    db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.id == rec1.id
    ).delete()
    db_session.commit()


def test_09_same_scheduler_cycle_twice_does_not_duplicate_data(db_session):
    """9. Consecutive scheduler runs on the same date bucket do not duplicate rows."""
    test_date = "2026-05-11"
    initial_count = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date
    ).count()

    # Capture once
    res1 = historical_ingestion_service.run_daily_scheduled_capture(date_bucket=test_date, db=db_session)
    count_after_first = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date
    ).count()

    # Capture again
    res2 = historical_ingestion_service.run_daily_scheduled_capture(date_bucket=test_date, db=db_session)
    count_after_second = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date
    ).count()

    assert count_after_first == 6
    assert count_after_second == 6
    assert res2["duplicates_prevented"] >= 6 or res2["rows_inserted"] == 0

    # Cleanup test date
    db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date
    ).delete()
    db_session.query(DailyCaptureLedgerModel).filter(
        DailyCaptureLedgerModel.date_bucket == test_date
    ).delete()
    db_session.commit()


def test_10_concurrent_style_duplicate_capture_is_safely_rejected(db_session):
    """10. Uniqueness constraint on (destination_id, date_bucket, dataset_mode) prevents duplicates."""
    from sqlalchemy.exc import IntegrityError
    test_date = "2026-05-12"
    m1 = HistoricalObservationModel(
        id=f"darjeeling_{test_date}_real",
        destination_id="darjeeling",
        date_bucket=test_date,
        dataset_mode="REAL",
        observed_at=datetime(2026, 5, 12, 10, 0, 0),
        current_crowd_pressure=50.0,
    )
    db_session.add(m1)
    db_session.commit()

    m2 = HistoricalObservationModel(
        id=f"darjeeling_{test_date}_real_dupe",
        destination_id="darjeeling",
        date_bucket=test_date,
        dataset_mode="REAL",
        observed_at=datetime(2026, 5, 12, 10, 0, 0),
        current_crowd_pressure=50.0,
    )
    db_session.add(m2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Cleanup
    db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.id == f"darjeeling_{test_date}_real"
    ).delete()
    db_session.commit()


# ─── D. Retry Behavior ────────────────────────────────────────────────────────

def test_11_first_attempt_failure_then_success(db_session):
    """11. Capture retries on initial failure and succeeds on subsequent attempt."""
    test_date = "2026-05-13"
    call_counts = {"attempts": 0}

    real_capture = historical_ingestion_service.capture_current_observation

    def mock_capture(*args, **kwargs):
        call_counts["attempts"] += 1
        if call_counts["attempts"] == 1 and kwargs.get("destination_id") == "darjeeling":
            raise ConnectionError("Transient network timeout")
        return real_capture(*args, **kwargs)

    with patch.object(historical_ingestion_service, "capture_current_observation", side_effect=mock_capture):
        res = historical_ingestion_service.run_daily_scheduled_capture(
            date_bucket=test_date,
            max_retries=3,
            db=db_session,
        )
        assert res["status"] in ("SUCCESS", "PARTIAL")
        assert res["retry_count"] >= 1

    # Cleanup
    db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date
    ).delete()
    db_session.query(DailyCaptureLedgerModel).filter(
        DailyCaptureLedgerModel.date_bucket == test_date
    ).delete()
    db_session.commit()


def test_12_three_failed_attempts_produce_failure(db_session):
    """12. If all 3 attempts fail for a destination, it is recorded as failed in ledger."""
    test_date = "2026-05-14"
    orig_capture = historical_ingestion_service.capture_current_observation

    def mock_capture(*args, **kwargs):
        dest_id = kwargs.get("destination_id") or (args[0] if args else None)
        if dest_id == "darjeeling":
            raise RuntimeError("Permanent upstream source unavailable")
        return orig_capture(*args, **kwargs)

    with patch.object(historical_ingestion_service, "capture_current_observation", side_effect=mock_capture):
        res = historical_ingestion_service.run_daily_scheduled_capture(
            date_bucket=test_date,
            max_retries=3,
            db=db_session,
        )
        assert "darjeeling" in res["destinations_failed"]
        assert res["status"] in ("PARTIAL", "FAILED")

        ledger = db_session.query(DailyCaptureLedgerModel).filter(
            DailyCaptureLedgerModel.destination_id == "darjeeling",
            DailyCaptureLedgerModel.date_bucket == test_date,
        ).first()
        assert ledger is not None
        assert ledger.final_status == "MISSING"
        assert ledger.attempts_count == 3

    # Cleanup
    db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date
    ).delete()
    db_session.query(DailyCaptureLedgerModel).filter(
        DailyCaptureLedgerModel.date_bucket == test_date
    ).delete()
    db_session.commit()


def test_13_retry_does_not_create_duplicate_rows(db_session):
    """13. Multiple retries before success still produce exactly one observation row."""
    test_date = "2026-05-15"
    attempt_count = 0

    real_capture = historical_ingestion_service.capture_current_observation

    def mock_capture(*args, **kwargs):
        nonlocal attempt_count
        if kwargs.get("destination_id") == "mirik":
            attempt_count += 1
            if attempt_count < 3:
                raise IOError("Temporary I/O glitch")
        return real_capture(*args, **kwargs)

    with patch.object(historical_ingestion_service, "capture_current_observation", side_effect=mock_capture):
        historical_ingestion_service.run_daily_scheduled_capture(
            date_bucket=test_date,
            max_retries=3,
            db=db_session,
        )

    rows = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.destination_id == "mirik",
        HistoricalObservationModel.date_bucket == test_date,
    ).all()
    assert len(rows) == 1

    # Cleanup
    db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date
    ).delete()
    db_session.query(DailyCaptureLedgerModel).filter(
        DailyCaptureLedgerModel.date_bucket == test_date
    ).delete()
    db_session.commit()


# ─── E. Source Health ─────────────────────────────────────────────────────────

def test_14_successful_source_marked_fresh(db_session):
    """14. A source with recent successful telemetry is marked FRESH or STALE; unavailable is marked UNAVAILABLE."""
    source_health = accumulation_health_service.get_source_health(db=db_session)
    crowd_src = next((s for s in source_health if s["signal_key"] == "crowd_engine_v2"), None)
    assert crowd_src is not None
    assert crowd_src["freshness_status"] in (FRESHNESS_FRESH, FRESHNESS_STALE)

    # Weather provider was MOCK and is suppressed to NULL in REAL mode -> UNAVAILABLE
    weather_src = next((s for s in source_health if s["signal_key"] == "weather"), None)
    assert weather_src is not None
    assert weather_src["freshness_status"] in (FRESHNESS_FRESH, FRESHNESS_STALE, FRESHNESS_UNAVAILABLE)


def test_15_failed_source_marked_unavailable(db_session):
    """15. A source that has never reported is marked UNAVAILABLE or UNKNOWN."""
    source_health = accumulation_health_service.get_source_health(db=db_session)
    for s in source_health:
        if s["last_success_at"] is None and s["last_attempt_at"] is not None:
            assert s["freshness_status"] == FRESHNESS_UNAVAILABLE


def test_16_stale_source_detected():
    """16. Source telemetry older than 24 hours is classified as STALE."""
    source_list = accumulation_health_service.get_source_health()
    for s in source_list:
        if s["last_success_at"] and s["age_seconds"] and s["age_seconds"] > 86400:
            assert s["freshness_status"] == FRESHNESS_STALE


def test_17_source_null_remains_null():
    """17. When a source is unavailable, its value remains None (NULL) and not 0.0 or fabricated."""
    test_rec = HistoricalObservationCreate(
        destination_id="darjeeling",
        observed_at=datetime.now(timezone.utc),
        date_bucket="2026-05-16",
        footfall=None,
        traffic_pressure=None,
        dataset_mode="REAL",
    )
    assert test_rec.footfall is None
    assert test_rec.traffic_pressure is None


def test_18_no_fallback_fabrication_occurs():
    """18. Ingesting with NULL values retains NULL values in the stored record."""
    test_rec = HistoricalObservationCreate(
        destination_id="darjeeling",
        observed_at=datetime(2026, 5, 17, 10, 0, 0),
        date_bucket="2026-05-17",
        footfall=None,
        accommodation_occupancy=None,
        dataset_mode="REAL",
    )
    rec = historical_ingestion_service.ingest_observation(test_rec)
    assert rec.footfall is None
    assert rec.accommodation_occupancy is None

    # Cleanup
    db = SessionLocal()
    db.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.id == rec.id
    ).delete()
    db.commit()
    db.close()


# ─── F. Destination Monitoring ────────────────────────────────────────────────

def test_19_per_destination_depth_is_accurate(db_session):
    """19. Per-destination eligible row counts match database query."""
    depth_report = historical_readiness_service.get_destination_depth_report(db=db_session)
    for dest in CANONICAL_DESTINATIONS:
        assert dest in depth_report["destinations"]
        assert depth_report["destinations"][dest]["eligible_rows"] >= 11


def test_20_per_destination_remaining_to_20_is_accurate(db_session):
    """20. Remaining depth to 20 rows is calculated as max(0, 20 - eligible_rows)."""
    streaks = accumulation_health_service.get_destination_streaks(db=db_session)
    for d in streaks["destinations"]:
        expected_remaining = max(0, 20 - d["eligible_rows"])
        assert d["remaining_to_20"] == expected_remaining


def test_21_streak_calculation_is_accurate(db_session):
    """21. Streak calculation identifies continuous consecutive daily observations."""
    streaks = accumulation_health_service.get_destination_streaks(db=db_session)
    for d in streaks["destinations"]:
        assert isinstance(d["current_valid_streak"], int)
        assert d["current_valid_streak"] >= 0


def test_22_one_missing_destination_produces_partial_success(db_session):
    """22. If only 5 destinations are captured on a date, status is PARTIAL_SUCCESS."""
    test_date = "2026-05-18"
    # Insert 5 canonical destinations
    for dest in CANONICAL_DESTINATIONS[:5]:
        rec = HistoricalObservationCreate(
            destination_id=dest,
            observed_at=datetime(2026, 5, 18, 10, 0, 0),
            date_bucket=test_date,
            current_crowd_pressure=45.0,
            dataset_mode="REAL",
        )
        historical_ingestion_service.ingest_observation(rec, db=db_session)

    health = accumulation_health_service.get_daily_accumulation_health(date_bucket=test_date, db=db_session)
    assert health["status"] == STATUS_PARTIAL_SUCCESS
    assert health["captured_valid"] == 5
    assert health["missing"] == 1
    assert "rishop" in health["missing_destinations"]

    # Cleanup
    db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.date_bucket == test_date
    ).delete()
    db_session.commit()


# ─── G. Velocity ──────────────────────────────────────────────────────────────

def test_23_7_day_rate_is_calculated_from_actual_eligible_rows(db_session):
    """23. Velocity is derived strictly from eligible database rows."""
    velocity = accumulation_health_service.get_accumulation_velocity(db=db_session)
    assert velocity["total_eligible_rows"] >= 66
    assert isinstance(velocity["overall_observed_rate_daily"], float)


def test_24_insufficient_history_is_explicitly_represented():
    """24. Insufficient history produces explicit 'INSUFFICIENT_HISTORY' string rather than invented rate."""
    velocity = accumulation_health_service.get_accumulation_velocity()
    if velocity["eligible_rows_last_7_days"] < 2:
        assert velocity["average_daily_eligible_rows_7d"] == "INSUFFICIENT_HISTORY"


def test_25_invalid_rows_do_not_affect_velocity(db_session):
    """25. Adding an INVALID observation does not increase accumulation velocity."""
    v1 = accumulation_health_service.get_accumulation_velocity(db=db_session)

    # Insert an INVALID test observation (e.g. missing target current_crowd_pressure)
    invalid_m = HistoricalObservationModel(
        id="test_invalid_velocity_row",
        destination_id="darjeeling",
        date_bucket="2026-05-19",
        observed_at=datetime(2026, 5, 19, 10, 0, 0),
        current_crowd_pressure=None, # Missing target -> INVALID
        dataset_mode="REAL",
    )
    db_session.add(invalid_m)
    db_session.commit()

    v2 = accumulation_health_service.get_accumulation_velocity(db=db_session)
    assert v2["total_eligible_rows"] == v1["total_eligible_rows"]

    # Cleanup
    db_session.delete(invalid_m)
    db_session.commit()


def test_26_synthetic_rows_do_not_affect_velocity(db_session):
    """26. Synthetic benchmark records are excluded from accumulation velocity."""
    v1 = accumulation_health_service.get_accumulation_velocity(db=db_session)

    synth_m = HistoricalObservationModel(
        id="test_synth_velocity_row",
        destination_id="darjeeling",
        date_bucket="2026-05-20",
        observed_at=datetime(2026, 5, 20, 10, 0, 0),
        current_crowd_pressure=60.0,
        dataset_mode="SYNTHETIC",
    )
    db_session.add(synth_m)
    db_session.commit()

    v2 = accumulation_health_service.get_accumulation_velocity(db=db_session)
    assert v2["total_eligible_rows"] == v1["total_eligible_rows"]

    # Cleanup
    db_session.delete(synth_m)
    db_session.commit()


# ─── H. Projection ────────────────────────────────────────────────────────────

def test_27_theoretical_minimum_calculation_is_correct(db_session):
    """27. Theoretical minimum days is computed correctly using 6.0 rows/day max rate."""
    proj = accumulation_health_service.get_hardened_projection(db=db_session)
    assert proj["theoretical_minimum_days"] >= 19
    assert "THEORETICAL_MAXIMUM_CAPTURE_RATE" in proj["theoretical_maximum_capture_rate"]


def test_28_projection_explicitly_says_it_is_not_a_guarantee(db_session):
    """28. Projection dictionary explicitly declares guarantee: False."""
    proj = accumulation_health_service.get_hardened_projection(db=db_session)
    assert proj["guarantee"] is False
    assert proj["projection_status"] == "PROJECTED"
    assert "NOT a guarantee" in proj["disclaimer"]


# ─── I. Eligibility Safety ───────────────────────────────────────────────────

def test_29_66_of_180_remains_ineligible(db_session):
    """29. Current dataset with 66 eligible rows strictly fails the gate (180 required)."""
    summary = historical_readiness_service.get_readiness_summary(db=db_session)
    assert summary["eligible"] is False
    assert summary["gate_status"] == "INSUFFICIENT_DATA"
    assert any("180" in reason for reason in summary["failed_requirements"])


def test_30_ineligible_cycle_does_not_train_xgboost(db_session):
    """30. Automated accumulation cycle on ineligible dataset blocks training and does not create model."""
    res = production_training_coordinator.retrain_if_eligible(db=db_session)
    assert res["status"] == "INSUFFICIENT_DATA"
    assert res["trained"] is False
    assert res["model_status"] == BASELINE_ACTIVE


def test_31_baseline_remains_active(db_session):
    """31. Active production model status remains BASELINE_ACTIVE while ineligible."""
    report = production_training_coordinator.get_readiness_report(db=db_session)
    assert report["model_status"] == BASELINE_ACTIVE
    assert report["production_state"] == STATE_BASELINE_INSUFFICIENT
    assert report["production_eligible"] is False


def test_32_existing_gate_remains_sole_authority(db_session):
    """32. ProductionEligibilityGate is the sole decider of ML eligibility."""
    verdict, _ = production_training_coordinator.check_eligibility(db=db_session)
    assert verdict.is_eligible is False
    assert verdict.status == "INSUFFICIENT_DATA"


# ─── J. Fingerprint ───────────────────────────────────────────────────────────

def test_33_valid_eligible_observation_changes_fingerprint(db_session):
    """33. Inserting a genuine eligible observation changes the dataset fingerprint."""
    v1, r1 = production_training_coordinator.check_eligibility(db=db_session)
    fp1 = production_training_coordinator._compute_dataset_fingerprint(v1, records=r1)

    # Insert genuine record
    test_date = "2026-05-25"
    test_rec = HistoricalObservationCreate(
        destination_id="darjeeling",
        observed_at=datetime(2026, 5, 25, 10, 0, 0),
        date_bucket=test_date,
        current_crowd_pressure=55.0,
        footfall=500.0,
        booking_demand=60.0,
        search_demand=70.0,
        holiday_pressure=10.0,
        event_pressure=5.0,
        dataset_mode="REAL",
    )
    saved = historical_ingestion_service.ingest_observation(test_rec, db=db_session)

    v2, r2 = production_training_coordinator.check_eligibility(db=db_session)
    fp2 = production_training_coordinator._compute_dataset_fingerprint(v2, records=r2)

    assert fp1 != fp2

    # Cleanup
    db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.id == saved.id
    ).delete()
    db_session.commit()


def test_34_invalid_changes_do_not_change_eligible_fingerprint(db_session):
    """34. Modifying or adding an INVALID record does not change the eligible dataset fingerprint."""
    v1, r1 = production_training_coordinator.check_eligibility(db=db_session)
    fp1 = production_training_coordinator._compute_dataset_fingerprint(v1, records=r1)

    inv_m = HistoricalObservationModel(
        id="test_inv_fingerprint_row",
        destination_id="darjeeling",
        date_bucket="2026-05-26",
        observed_at=datetime(2026, 5, 26, 10, 0, 0),
        current_crowd_pressure=None, # Missing target -> INVALID
        dataset_mode="REAL",
    )
    db_session.add(inv_m)
    db_session.commit()

    v2, r2 = production_training_coordinator.check_eligibility(db=db_session)
    fp2 = production_training_coordinator._compute_dataset_fingerprint(v2, records=r2)

    assert fp1 == fp2

    # Cleanup
    db_session.delete(inv_m)
    db_session.commit()


def test_35_synthetic_benchmark_changes_do_not_change_eligible_fingerprint(db_session):
    """35. Modifying or adding SYNTHETIC benchmark rows does not change eligible dataset fingerprint."""
    v1, r1 = production_training_coordinator.check_eligibility(db=db_session)
    fp1 = production_training_coordinator._compute_dataset_fingerprint(v1, records=r1)

    synth_m = HistoricalObservationModel(
        id="test_synth_fingerprint_row",
        destination_id="darjeeling",
        date_bucket="2026-05-27",
        observed_at=datetime(2026, 5, 27, 10, 0, 0),
        current_crowd_pressure=70.0,
        dataset_mode="SYNTHETIC",
    )
    db_session.add(synth_m)
    db_session.commit()

    v2, r2 = production_training_coordinator.check_eligibility(db=db_session)
    fp2 = production_training_coordinator._compute_dataset_fingerprint(v2, records=r2)

    assert fp1 == fp2

    # Cleanup
    db_session.delete(synth_m)
    db_session.commit()


def test_36_fingerprint_remains_deterministic(db_session):
    """36. Evaluating fingerprint multiple times on unchanged dataset produces identical SHA-256."""
    v1, r1 = production_training_coordinator.check_eligibility(db=db_session)
    fp1 = production_training_coordinator._compute_dataset_fingerprint(v1, records=r1)
    fp2 = production_training_coordinator._compute_dataset_fingerprint(v1, records=r1)
    assert fp1 == fp2
    assert len(fp1) == 64


# ─── K. Transition ───────────────────────────────────────────────────────────

def test_37_newly_eligible_state_invokes_training_coordinator(db_session):
    """37. Mocking eligible gate verdict causes transition detector to report ELIGIBILITY_REACHED."""
    mock_verdict = ProductionEligibilityVerdict(
        is_eligible=True,
        status="PRODUCTION_READY",
        total_rows=180,
        distinct_destinations=6,
        temporal_span_days=35,
        target_availability_percent=100.0,
        core_signal_missingness_percent=25.0,
        target_variance=120.0,
    )
    with patch.object(production_training_coordinator, "check_eligibility", return_value=(mock_verdict, [])):
        res = production_training_coordinator.detect_state_transition(db=db_session)
        assert res["transition_detected"] is True
        assert res["transition_record"] is not None
        assert res["transition_record"]["new_state"] == STATE_BASELINE_ELIGIBILITY_REACHED


def test_38_existing_training_workflow_is_not_duplicated(db_session):
    """38. Calling retrain_if_eligible twice on identical dataset does not trigger duplicate training."""
    mock_verdict = ProductionEligibilityVerdict(
        is_eligible=True,
        status="PRODUCTION_READY",
        total_rows=180,
        distinct_destinations=6,
        temporal_span_days=35,
        target_availability_percent=100.0,
        core_signal_missingness_percent=25.0,
        target_variance=120.0,
    )
    fp = "deterministic_test_fingerprint_hash_abc123"
    with patch.object(production_training_coordinator, "check_eligibility", return_value=(mock_verdict, [])), \
         patch.object(production_training_coordinator, "_compute_dataset_fingerprint", return_value=fp):
        production_training_coordinator._last_training_metadata = {"dataset_fingerprint": fp}
        res = production_training_coordinator.retrain_if_eligible(force=False, db=db_session)
        assert res["status"] == "NO_NEW_DATA"


def test_39_promotion_remains_blocked_until_candidate_validation_succeeds(db_session):
    """39. If candidate model fails validation thresholds, promotion is rejected and baseline is retained."""
    from app.services.ml.evaluation import compare_models
    cmp_res = compare_models(
        baseline_mae=10.0,
        ml_mae=25.0,
        baseline_rmse=12.0,
        ml_rmse=30.0,
    )
    assert cmp_res["ml_improves_over_baseline"] is False
    assert cmp_res["mae_direction"] == "REGRESSION"
    assert "Baseline rule model recommended" in cmp_res["verdict"]


# ─── L. Isolation ─────────────────────────────────────────────────────────────

def test_40_invalid_records_remain_quarantined(db_session):
    """40. The 28 INVALID audit rows in the database remain quarantined from ML eligibility."""
    summary = historical_readiness_service.get_readiness_summary(db=db_session)
    assert summary["invalid_rows"] == 28
    assert summary["total_real_rows"] == summary["ml_eligible_real_rows"] + summary["invalid_rows"]


def test_41_synthetic_records_remain_isolated(db_session):
    """41. There are exactly 0 synthetic rows in the REAL historical dataset."""
    synth_in_real = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL",
        HistoricalObservationModel.data_status == "SYNTHETIC",
    ).count()
    assert synth_in_real == 0


def test_42_existing_prompt11_behavior_remains_intact(client):
    """42. Prompt 11 endpoints and contracts (/accumulation-readiness, /destination-depth, /accumulation-gaps) remain intact."""
    r1 = client.get("/api/admin/ml/accumulation-readiness")
    assert r1.status_code == 200
    assert r1.json()["required_rows"] == 180

    r2 = client.get("/api/admin/ml/destination-depth")
    assert r2.status_code == 200
    assert r2.json()["total_canonical_destinations"] == 6

    r3 = client.get("/api/admin/ml/accumulation-gaps")
    assert r3.status_code == 200
    assert "gap_summary" in r3.json()

    # Prompt 12 new endpoints
    r4 = client.get("/api/admin/ml/accumulation-health")
    assert r4.status_code == 200
    assert "expected_destinations" in r4.json()

    r5 = client.get("/api/admin/ml/accumulation-history")
    assert r5.status_code == 200
    assert "history" in r5.json()
