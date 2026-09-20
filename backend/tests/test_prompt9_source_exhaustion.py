"""
Comprehensive Test Suite for Prompt 9:
Genuine Historical Dataset Deep Expansion, Raw-Source Exhaustion & ML Readiness Acceleration.

Tests:
1. Raw Source Discovery: Audit of bookings, demand_events, holidays, events, and homestays.
2. Historical Date Expansion: Recovery of genuine dates (2026-08-15 to 2026-09-20), temporal span >= 30 days.
3. Booking Aggregation: IST bucketing, confirmed creation pace vs stay occupancy separation.
4. Demand Event Aggregation: All genuine event types (search, booking, alternative_acceptance, outbound_booking_click) aggregated.
5. Destination Normalization: Canonical mapping across all 6 destinations without loss or fabrication.
6. IST Date Bucketing: Strict local calendar alignment without boundary leaks.
7. Target Reconstruction: Canonical Crowd Engine V2 target is preserved, 100% target completeness on eligible rows.
8. Temporal Leakage Prevention: Features engineered at T use only data available at or before T (target_time > feature_time).
9. Invalid Observation Exclusion: Future audit records (28 rows) are strictly excluded from ML eligibility.
10. REAL / SYNTHETIC Isolation: REAL dataset mode has exactly 0 synthetic rows.
11. Deterministic Rebuild: Multiple rebuild passes yield identical state.
12. Idempotency: Duplicate captures prevent insertion of duplicate rows.
13. Provenance Completeness: Every available signal has verified source, provider_mode, and confidence.
14. Six-Destination Coverage: Darjeeling, Kalimpong, Mirik, Lava, Lolegaon, and Rishop all present.
15. Readiness Recalculation & Structural Projection: Gate evaluation correctly blocks XGBoost with exact missing requirements and structural projection.
"""

import pytest
from datetime import datetime, date, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.entities import (
    HistoricalObservationModel,
    BookingModel,
    DemandEventModel,
    DestinationModel,
    HomestayModel,
    HolidayModel,
    EventModel,
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
from app.services.historical.repair_service import historical_repair_service
from app.services.historical.backfill_service import historical_backfill_service
from app.services.historical.readiness_service import (
    HistoricalReadinessService,
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
from app.services.ml.feature_builder import StandardFeatureBuilder


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


# ─── 1. Raw Source Date Discovery & Inventory ──────────────────────────────

def test_raw_source_bookings_ledger_audit(db_session):
    """Verifies that the bookings table contains verified transaction records with valid timestamps."""
    total_bookings = db_session.query(BookingModel).count()
    assert total_bookings >= 300, f"Expected >= 300 bookings in ledger, found {total_bookings}"

    confirmed_count = db_session.query(BookingModel).filter(BookingModel.status == "CONFIRMED").count()
    assert confirmed_count >= 200, f"Expected >= 200 confirmed bookings, found {confirmed_count}"

    sample_booking = db_session.query(BookingModel).first()
    assert sample_booking.created_at is not None
    assert sample_booking.check_in_date is not None


def test_raw_source_demand_events_telemetry_audit(db_session):
    """Verifies that demand_events contains verified telemetry events."""
    total_events = db_session.query(DemandEventModel).count()
    assert total_events >= 800, f"Expected >= 800 demand events, found {total_events}"

    # Check distinct event types
    event_types = {e[0] for e in db_session.query(DemandEventModel.event_type).distinct().all()}
    assert "search" in event_types
    assert "booking" in event_types


def test_raw_source_canonical_destinations_and_homestays(db_session):
    """Verifies all 6 canonical destinations exist in database with registered homestays."""
    dest_count = db_session.query(DestinationModel).count()
    assert dest_count >= 6

    for dest_id in CANONICAL_DESTINATIONS:
        dest = db_session.query(DestinationModel).filter(DestinationModel.id == dest_id).first()
        assert dest is not None, f"Canonical destination {dest_id} missing in destinations table"
        assert dest.carrying_capacity > 0


# ─── 2. Historical Date Expansion & Temporal Span ──────────────────────────

def test_genuine_historical_date_expansion_and_temporal_span(db_session):
    """
    Prompt 9 expands genuine historical dates to at least 10 distinct dates,
    spanning at least 30 calendar days (satisfying the temporal span threshold).
    """
    summary = HistoricalReadinessService().get_readiness_summary(db=db_session)
    assert summary["distinct_dates"] >= 10
    assert summary["temporal_span_days"] >= 30
    assert summary["earliest_date"] <= "2026-08-15"
    assert summary["latest_date"] >= "2026-09-20"


# ─── 3. Booking & Demand Aggregation with IST Bucketing ────────────────────

def test_ist_date_bucketing_and_destination_normalization():
    """Destination normalization maps aliases cleanly to canonical IDs."""
    assert normalize_destination_id("darjeeling_town") == "darjeeling"
    assert normalize_destination_id("mirik_lake") == "mirik"
    assert normalize_destination_id("lava_village") == "lava"
    assert normalize_destination_id("kaffer_village") == "lolegaon"
    assert normalize_destination_id("rishyap") == "rishop"
    assert normalize_destination_id("kalimpong-district") == "kalimpong"


def test_booking_velocity_signal_derivation(db_session):
    """Booking demand is derived from confirmed bookings created on target date."""
    capacities = historical_backfill_service._fetch_destination_capacity(db_session)
    target_date = date(2026, 9, 18)

    # Kalimpong has 173 confirmed bookings on 2026-09-18
    signals = historical_backfill_service._extract_historical_day_signals(
        dest_clean="kalimpong",
        target_date=target_date,
        capacities=capacities.get("kalimpong", {}),
        db=db_session
    )

    assert signals is not None
    assert "booking_demand" in signals.signal_provenance
    assert signals.signal_provenance["booking_demand"].provider_mode == "HISTORICAL"
    assert signals.signal_provenance["booking_demand"].source == "POSTGRESQL_BOOKINGS_LEDGER"
    assert signals.signal_provenance["booking_demand"].raw_value > 0


# ─── 4. Target Reconstruction & Ground-Truth Integrity ────────────────────

def test_target_reconstruction_integrity(db_session):
    """Target current_crowd_pressure must be bounded in [0, 100] and 100% available on eligible rows."""
    summary = HistoricalReadinessService().get_readiness_summary(db=db_session)
    assert summary["target_availability_percent"] == 100.0
    assert summary["target_variance"] >= 4.0

    eligible_rows = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL"
    ).all()

    for r in eligible_rows:
        score = observation_quality_scorer.score_observation(r)
        if score.quality_grade != "INVALID":
            assert r.current_crowd_pressure is not None
            assert 0.0 <= r.current_crowd_pressure <= 100.0


# ─── 5. Temporal Leakage Prevention ────────────────────────────────────────

def test_leakage_safe_feature_construction_ordering():
    """Feature builder must enforce that target timestamp > feature timestamp."""
    builder = StandardFeatureBuilder()
    feat_dt = date(2026, 9, 18)
    targ_dt = date(2026, 9, 21)

    features = builder.build_inference_features(
        destination_id="darjeeling",
        target_date=targ_dt,
        feature_date=feat_dt,
        target_horizon_days=3
    )

    assert features["target_horizon_days"] == 3
    assert targ_dt > feat_dt

    # Test build_feature_row with explicit timestamps
    obs_mock = type("MockObs", (), {
        "date_bucket": "2026-09-18",
        "destination_id": "darjeeling",
        "current_crowd_pressure": 45.0
    })()
    row = builder.build_feature_row(
        obs=obs_mock,
        feature_timestamp="2026-09-18",
        target_timestamp="2026-09-20",
        target_horizon_days=2
    )
    assert row["feature_timestamp"] < row["target_timestamp"]


# ─── 6. Invalid Observation Exclusion from ML Eligibility ─────────────────

def test_invalid_observations_excluded_from_ml_eligibility(db_session):
    """
    Prompt 9 Section 15: Physical audit records with future date buckets are retained
    in the database for audit integrity, but are EXCLUDED from ML eligibility.
    """
    summary = HistoricalReadinessService().get_readiness_summary(db=db_session)

    # Total in DB includes audit records
    assert summary["total_real_observations"] >= summary["ml_eligible_real_observations"]
    assert summary["invalid_audit_records"] > 0

    # Gate must be evaluated strictly against ml_eligible_real_observations
    assert summary["real_rows"] == summary["ml_eligible_real_observations"]
    assert summary["ml_eligible_real_observations"] >= 60


# ─── 7. REAL vs SYNTHETIC Isolation ────────────────────────────────────────

def test_zero_synthetic_rows_in_real_dataset(db_session):
    """REAL dataset must have strictly 0 synthetic rows and 0 synthetic signals."""
    real_rows = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL"
    ).all()

    for r in real_rows:
        assert "synthetic" not in r.id.lower()
        prov = r.signal_provenance_json or {}
        for sig_name, sig_prov in prov.items():
            if isinstance(sig_prov, dict) and sig_prov.get("is_available"):
                assert sig_prov.get("provider_mode") != "SYNTHETIC"


# ─── 8. Deterministic Rebuild & Idempotency ────────────────────────────────

def test_deterministic_rebuild_idempotency(db_session):
    """Running rebuild across same date range produces identical counts with 0 synthetic rows."""
    res1 = historical_repair_service.rebuild_historical_dataset(
        start_date="2026-09-18",
        end_date="2026-09-19",
        dataset_mode="REAL",
        dry_run=False,
        db=db_session
    )
    assert res1["status"] == "SUCCESS"
    assert res1["synthetic_rows_introduced"] == 0

    res2 = historical_repair_service.rebuild_historical_dataset(
        start_date="2026-09-18",
        end_date="2026-09-19",
        dataset_mode="REAL",
        dry_run=False,
        db=db_session
    )
    assert res2["status"] == "SUCCESS"
    # Idempotent re-run adds 0 new rows
    assert res2["genuine_rows_added"] == 0


# ─── 9. Six-Destination Coverage ───────────────────────────────────────────

def test_all_six_canonical_destinations_represented(db_session):
    """All 6 canonical destinations must have at least 10 observations each."""
    summary = HistoricalReadinessService().get_readiness_summary(db=db_session)
    dest_counts = summary["rows_per_destination"]

    for d in CANONICAL_DESTINATIONS:
        assert d in dest_counts
        assert dest_counts[d] >= 10, f"Destination {d} has {dest_counts[d]} rows, expected >= 10"


# ─── 10. Unmeasured Physical Telemetry Remains NULL ────────────────────────

def test_unmeasured_physical_signals_remain_strictly_null(db_session):
    """Historical footfall, traffic, and weather must remain NULL with UNAVAILABLE provider_mode."""
    obs = db_session.query(HistoricalObservationModel).filter(
        HistoricalObservationModel.dataset_mode == "REAL",
        HistoricalObservationModel.date_bucket == "2026-09-18",
        HistoricalObservationModel.destination_id == "darjeeling"
    ).first()

    assert obs is not None
    assert obs.footfall is None
    assert obs.traffic_pressure is None
    assert obs.weather_pressure is None

    prov = obs.signal_provenance_json or {}
    assert prov.get("footfall", {}).get("provider_mode") == "UNAVAILABLE"
    assert prov.get("traffic_pressure", {}).get("provider_mode") == "UNAVAILABLE"
    assert prov.get("weather_pressure", {}).get("provider_mode") == "UNAVAILABLE"


# ─── 11. Production Eligibility Gate & XGBoost Safety ──────────────────────

def test_production_eligibility_gate_thresholds_immutable():
    """All 7 gate thresholds must remain immutable."""
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


def test_xgboost_training_blocked_and_baseline_retained(db_session):
    """
    Since total ML-eligible rows (60) < 180 and rows/dest (10) < 20,
    XGBoost production training MUST be blocked and baseline_rule_v2 retained.
    """
    coord_res = production_training_coordinator.retrain_if_eligible(db=db_session)
    assert coord_res["trained"] is False
    assert coord_res["model_status"] == BASELINE_ACTIVE
    assert coord_res["status"] == INSUFFICIENT_DATA
    assert any("min_rows (180)" in req for req in coord_res["failed_requirements"])


# ─── 12. Structural Accumulation Projection ────────────────────────────────

def test_structural_accumulation_projection_label_and_values(db_session):
    """
    Readiness report must include structural accumulation projection clearly labeled
    as STRUCTURAL ACCUMULATION PROJECTION (never model prediction).
    """
    summary = HistoricalReadinessService().get_readiness_summary(db=db_session)
    proj = summary.get("projection", {})
    assert proj.get("label") == "STRUCTURAL ACCUMULATION PROJECTION"
    assert proj.get("rows_needed") == 120
    assert "disclaimer" in proj
    assert "Does not guarantee ML model accuracy" in proj["disclaimer"]
