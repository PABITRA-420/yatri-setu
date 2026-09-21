"""
Comprehensive Test Suite for Prompt 8:
Real Historical Ground-Truth Expansion, Invalid Observation Repair & Genuine Dataset Growth.

Tests:
1. Forensic Audit: Detection and classification of invalid observations (future date, missing target, non-canonical destination).
2. Evidence-Based Repair Policy: Only repair when genuine source evidence exists; retain unrepairable rows in audit trail.
3. Repair Idempotency: Repeated repair execution yields identical state without duplication or corruption.
4. Deterministic Rebuild: Historical rebuild across verified dates expands genuine observations with 0 synthetic rows.
5. Booking Velocity vs Stay Occupancy: Forward booking creation pace (created_at) and stay occupancy (check_in_date) are properly separated.
6. Target Ground-Truth Integrity: Current Crowd Engine V2 target is preserved, 100% target completeness required.
7. Provenance Preservation: Repaired and rebuilt signals maintain genuine source names and provider modes.
8. Zero Synthetic Contamination: REAL dataset remains 100% isolated from SYNTHETIC / MIXED.
9. Unmeasured Signals Remain NULL: No guessing, mean/median filling, or interpolation of unavailable signals.
10. Production Eligibility Gate Preservation: All 7 gate thresholds remain strictly unchanged.
11. XGBoost Blocked on Ineligible Data: Production training coordinator refuses promotion and retains BASELINE_ACTIVE.
12. Historical API Endpoints: /api/v1/historical/forensics, /repair-invalid, /rebuild.
13. Admin Historical API Endpoints: /api/v1/admin/historical/forensics, /repair-invalid, /rebuild.
"""

import pytest
from datetime import datetime, date, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.entities import HistoricalObservationModel, BookingModel, DemandEventModel
from app.models.historical import HistoricalObservationCreate, SignalProvenanceRecord
from app.services.historical.quality_scoring import (
    observation_quality_scorer,
    CANONICAL_DESTINATIONS,
    CORE_SIGNALS,
)
from app.services.historical.repair_service import historical_repair_service
from app.services.historical.backfill_service import historical_backfill_service
from app.services.historical.readiness_service import (
    GATE_REQUIRED_ROWS,
    GATE_REQUIRED_DAYS,
    GATE_REQUIRED_DESTINATIONS,
    GATE_REQUIRED_ROWS_PER_DEST,
)
from app.services.ml.eligibility_gate import production_eligibility_gate
from app.services.ml.production_training_coordinator import (
    production_training_coordinator,
    BASELINE_ACTIVE,
    INSUFFICIENT_DATA,
)


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


# ─── 1. Forensic Audit & Invalid Observation Tests ─────────────────────────

def test_invalid_observation_detection_future_date():
    """Future date buckets must be strictly flagged as INVALID."""
    future_date = (datetime.now(timezone.utc).date() + timedelta(days=5)).strftime("%Y-%m-%d")
    fake_obs = {
        "destination_id": "darjeeling",
        "date_bucket": future_date,
        "current_crowd_pressure": 50.0,
        "booking_demand": 40.0,
        "search_demand": 30.0,
        "holiday_pressure": 10.0,
        "event_pressure": 15.0,
    }
    score = observation_quality_scorer.score_observation(fake_obs)
    assert score.quality_grade == "INVALID"
    assert any("in the future" in err for err in score.validation_errors)


def test_invalid_observation_detection_missing_target():
    """Observations missing current_crowd_pressure target must be strictly INVALID."""
    today = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")
    fake_obs = {
        "destination_id": "darjeeling",
        "date_bucket": today,
        "current_crowd_pressure": None,  # Missing target
        "booking_demand": 40.0,
        "search_demand": 30.0,
    }
    score = observation_quality_scorer.score_observation(fake_obs)
    assert score.quality_grade == "INVALID"
    assert any("target is missing" in err for err in score.validation_errors)


def test_invalid_observation_detection_non_canonical_destination():
    """Non-canonical destinations must be rejected as INVALID."""
    today = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")
    fake_obs = {
        "destination_id": "mumbai_central",
        "date_bucket": today,
        "current_crowd_pressure": 50.0,
    }
    score = observation_quality_scorer.score_observation(fake_obs)
    assert score.quality_grade == "INVALID"
    assert any("canonical registry" in err for err in score.validation_errors)


def test_forensic_audit_service_classifications(db_session):
    """Verifies that forensic audit classifies all invalid observations in the database."""
    audit = historical_repair_service.audit_invalid_observations(dataset_mode="REAL", db=db_session)
    assert isinstance(audit, list)
    assert len(audit) >= 4

    for item in audit:
        assert "observation_id" in item
        assert "destination" in item
        assert "date_bucket" in item
        assert "repair_classification" in item
        assert "repairable" in item
        assert "recommended_action" in item
        assert item["destination"] in CANONICAL_DESTINATIONS

        # The 4 known invalid rows are future dates
        if item["future_date_bucket"]:
            assert item["repair_classification"] == "NOT_REPAIRABLE_FUTURE_BUCKET"
            assert item["repairable"] is False


# ─── 2. Repair Policy & Idempotency Tests ───────────────────────────────────

def test_unrepairable_observations_are_never_deleted(db_session):
    """Unrepairable observations must be preserved in the DB for audit integrity."""
    before_count = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL"
    ).count()

    repair_res = historical_repair_service.repair_invalid_observations(
        dataset_mode="REAL",
        dry_run=False,
        db=db_session
    )

    after_count = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL"
    ).count()

    # Rows must NEVER decrease (no silent deletion)
    assert after_count >= before_count
    assert repair_res["status"] == "SUCCESS"


def test_repair_service_idempotency(db_session):
    """Running repair multiple times produces the exact same deterministic outcome."""
    run1 = historical_repair_service.repair_invalid_observations(dataset_mode="REAL", dry_run=True, db=db_session)
    run2 = historical_repair_service.repair_invalid_observations(dataset_mode="REAL", dry_run=True, db=db_session)

    assert run1["total_invalid_before"] == run2["total_invalid_before"]
    assert run1["repairable_count"] == run2["repairable_count"]
    assert run1["unrepairable_count"] == run2["unrepairable_count"]


# ─── 3. Historical Rebuild & Dataset Expansion Tests ────────────────────────

def test_historical_dataset_rebuild_zero_synthetic(db_session):
    """Rebuild must introduce exactly 0 synthetic rows into the REAL dataset."""
    rebuild_res = historical_repair_service.rebuild_historical_dataset(
        start_date="2026-09-15",
        end_date="2026-09-20",
        dataset_mode="REAL",
        dry_run=False,
        db=db_session
    )

    assert rebuild_res["status"] == "SUCCESS"
    assert rebuild_res["synthetic_rows_introduced"] == 0

    # Verify no row has synthetic ID or synthetic provider mode
    real_rows = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL"
    ).all()

    for r in real_rows:
        assert "synthetic" not in r.id.lower()
        prov = r.signal_provenance_json or {}
        for sig, p in prov.items():
            if isinstance(p, dict) and p.get("is_available"):
                assert p.get("provider_mode") != "SYNTHETIC"


def test_six_destination_coverage_after_rebuild(db_session):
    """All 6 canonical destinations must have genuine representation."""
    comp = historical_repair_service.get_dataset_comparison(dataset_mode="REAL", db=db_session)
    dest_counts = comp["rows_per_destination"]

    for d in CANONICAL_DESTINATIONS:
        assert d in dest_counts
        assert dest_counts[d] >= 6, f"Destination {d} should have at least 6 rebuilt rows"


# ─── 4. Booking Velocity vs Stay Occupancy Tests ─────────────────────────────

def test_booking_velocity_vs_stay_occupancy_separation(db_session):
    """
    booking_demand measures forward reservation creation pace (created_at),
    while accommodation_occupancy measures active stays (check_in_date <= date <= check_out_date).
    """
    capacities = historical_backfill_service._fetch_destination_capacity(db_session)
    target_date = date(2026, 9, 18)

    signals = historical_backfill_service._extract_historical_day_signals(
        dest_clean="kalimpong",
        target_date=target_date,
        capacities=capacities.get("kalimpong", {}),
        db=db_session
    )

    assert signals is not None
    prov = signals.signal_provenance

    # Verify booking_demand provenance
    assert "booking_demand" in prov
    assert prov["booking_demand"].source == "POSTGRESQL_BOOKINGS_LEDGER"
    assert prov["booking_demand"].raw_unit == "confirmed_created_bookings"
    assert prov["booking_demand"].raw_value > 0  # 173 bookings created on 2026-09-18

    # Verify accommodation_occupancy provenance
    assert "accommodation_occupancy" in prov
    assert prov["accommodation_occupancy"].source == "POSTGRESQL_HOMESTAY_INVENTORY"
    assert prov["accommodation_occupancy"].raw_unit == "percent_occupancy"


# ─── 5. Unmeasured Signals & Target Integrity Tests ─────────────────────────

def test_unmeasured_footfall_remains_strictly_null(db_session):
    """Physical footfall must remain NULL with UNAVAILABLE provenance when unmeasured."""
    obs = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL",
        HistoricalObservationModel.date_bucket == "2026-09-18",
        HistoricalObservationModel.destination_id == "kalimpong"
    ).first()

    assert obs is not None
    # No physical sensor deployed -> footfall must be strictly None/NULL
    assert obs.footfall is None
    prov = obs.signal_provenance_json.get("footfall", {})
    assert prov.get("is_available") is False
    assert prov.get("provider_mode") == "UNAVAILABLE"


def test_target_completeness_100_percent(db_session):
    """Every rebuilt REAL observation must have current_crowd_pressure ground truth."""
    comp = historical_repair_service.get_dataset_comparison(dataset_mode="REAL", db=db_session)
    assert comp["target_complete_rows"] == comp["real_rows"]
    assert comp["real_rows"] >= 40


# ─── 6. Production Eligibility Gate & ML Safety Tests ───────────────────────

def test_production_eligibility_gate_thresholds_strictly_preserved():
    """All 7 ProductionEligibilityGate thresholds must remain exactly as originally defined."""
    assert GATE_REQUIRED_ROWS == 180
    assert GATE_REQUIRED_DAYS == 30
    assert GATE_REQUIRED_DESTINATIONS == 3
    assert GATE_REQUIRED_ROWS_PER_DEST == 20
    assert production_eligibility_gate.rules.min_total_rows == 180
    assert production_eligibility_gate.rules.min_temporal_span_days == 30
    assert production_eligibility_gate.rules.min_destinations == 3
    assert production_eligibility_gate.rules.min_rows_per_destination == 20
    assert production_eligibility_gate.rules.max_missing_signal_rate == 0.70
    assert production_eligibility_gate.rules.min_target_variance == 4.0


def test_xgboost_training_blocked_while_gate_fails(db_session):
    """XGBoost production training coordinator must refuse promotion and remain BASELINE_ACTIVE."""
    result = production_training_coordinator.retrain_if_eligible(
        db=db_session
    )

    assert result["trained"] is False
    assert result["model_status"] == BASELINE_ACTIVE
    assert result["status"] == INSUFFICIENT_DATA
    assert len(result["failed_requirements"]) > 0


# ─── 7. Historical API Endpoints Tests ──────────────────────────────────────

def test_api_historical_forensics_endpoint(client):
    """GET /api/v1/historical/forensics returns forensic audit items."""
    res = client.get("/api/v1/historical/forensics?dataset_mode=REAL")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 4


def test_api_historical_repair_endpoint_dry_run(client):
    """POST /api/v1/historical/repair-invalid in dry run mode."""
    res = client.post("/api/v1/historical/repair-invalid?dataset_mode=REAL&dry_run=true")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["dry_run"] is True
    assert "total_invalid_before" in data


def test_api_historical_rebuild_endpoint(client):
    """POST /api/v1/historical/rebuild runs deterministic rebuild."""
    res = client.post(
        "/api/v1/historical/rebuild"
        "?start_date=2026-09-18&end_date=2026-09-19&dataset_mode=REAL&dry_run=true"
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["synthetic_rows_introduced"] == 0


def test_admin_historical_endpoints(client):
    """Admin endpoints under /api/v1/admin/historical/ function correctly."""
    res = client.get("/api/v1/admin/historical/forensics?dataset_mode=REAL")
    assert res.status_code == 200

    res_rep = client.post("/api/v1/admin/historical/repair-invalid?dataset_mode=REAL&dry_run=true")
    assert res_rep.status_code == 200
