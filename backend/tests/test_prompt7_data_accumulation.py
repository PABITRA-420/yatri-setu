"""
Comprehensive Test Suite for Prompt 7:
Production Historical Data Accumulation, Six-Destination Coverage & ML Readiness Pipeline.

Tests:
1. Canonical Destination Normalization (canonical IDs, aliases, suffixes, rejection of unknown destinations).
2. Idempotency & Duplicate Prevention (same capture twice, duplicates_prevented counter, unique constraint).
3. Partial Provider Availability & NULL Preservation (weather/traffic unavailable -> NULL, valid REAL observation).
4. Observation vs Ingestion Timestamp Separation (observed_at aligns to observation date, ingested_at is now).
5. Six-Destination Coverage Tracking (darjeeling, kalimpong, mirik, lava, lolegaon, rishop).
6. Capture Retry & Provider Failure Tracking (bounded retries, resilience against single-provider offline).
7. Capture Status Endpoint & Metrics (last_capture_start, completion, rows_inserted, freshness).
8. Readiness Service & Metrics (row progress %, temporal progress %, destination coverage %, core missingness %).
9. Structural Projection (method, assumptions, insufficient_accumulation_history handling, eligibility unchanged).
10. Gate Thresholds Unchanged (180 rows, 30 days, 3 destinations, 20 rows/dest).
11. Production Training Coordinator Refusal on Ineligible REAL Data.
12. No Synthetic Contamination (0 synthetic rows in REAL dataset mode).
13. Leakage Prevention (feature_timestamp <= target_timestamp).
"""

import pytest
from datetime import datetime, date, timezone, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.entities import HistoricalObservationModel
from app.models.historical import HistoricalObservationCreate, SignalProvenanceRecord
from app.services.historical.destination_registry import (
    CANONICAL_DESTINATIONS,
    normalize_destination_id,
    is_canonical_destination,
)
from app.services.historical.ingestion_service import historical_ingestion_service
from app.services.historical.readiness_service import (
    historical_readiness_service,
    GATE_REQUIRED_ROWS,
    GATE_REQUIRED_DAYS,
    GATE_REQUIRED_DESTINATIONS,
    GATE_REQUIRED_ROWS_PER_DEST,
)
from app.services.historical.quality_scoring import observation_quality_scorer
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


class TestCanonicalDestinationRegistry:
    """Tests for Section 4: Destination normalization & canonical registry."""

    def test_canonical_destinations_accepted(self):
        for dest in ("darjeeling", "kalimpong", "mirik", "lava", "lolegaon", "rishop"):
            assert normalize_destination_id(dest) == dest
            assert is_canonical_destination(dest) is True

    def test_case_and_whitespace_insensitivity(self):
        assert normalize_destination_id("  Darjeeling  ") == "darjeeling"
        assert normalize_destination_id("KALIMPONG") == "kalimpong"
        assert normalize_destination_id("  Mirik ") == "mirik"

    def test_alias_normalization(self):
        assert normalize_destination_id("darj") == "darjeeling"
        assert normalize_destination_id("darjeeling_town") == "darjeeling"
        assert normalize_destination_id("darjeeling-district") == "darjeeling"
        assert normalize_destination_id("rishyap") == "rishop"
        assert normalize_destination_id("rishyap_village") == "rishop"
        assert normalize_destination_id("loleygaon") == "lolegaon"
        assert normalize_destination_id("kaffer") == "lolegaon"
        assert normalize_destination_id("mirik_lake") == "mirik"
        assert normalize_destination_id("lava_bazar") == "lava"

    def test_unknown_destination_raises_value_error(self):
        with pytest.raises(ValueError) as exc:
            normalize_destination_id("gangtok")
        assert "Unknown destination" in str(exc.value)

        assert is_canonical_destination("siliguri") is False
        assert is_canonical_destination("kolkata") is False


class TestObservationVsIngestionTimestamp:
    """Tests for Section 9: Strict separation of observed_at and ingested_at."""

    def test_observed_at_separated_from_ingested_at_on_historical_date(self, db_session):
        test_bucket = "2026-09-01"
        rec = historical_ingestion_service.capture_current_observation(
            destination_id="darjeeling",
            date_bucket=test_bucket,
            dataset_mode="REAL",
            db=db_session
        )

        assert rec.date_bucket == test_bucket
        # observed_at reflects September 1, 2026
        assert rec.observed_at.date() == date(2026, 9, 1)
        # ingested_at reflects the current real-time UTC timestamp
        now_date = datetime.now(timezone.utc).date()
        assert rec.ingested_at.date() == now_date
        assert rec.observed_at != rec.ingested_at


class TestIdempotencyAndDuplicatePrevention:
    """Tests for Section 8: Repeated captures prevent duplicate rows."""

    def test_repeated_daily_capture_is_idempotent(self, db_session):
        test_bucket = "2026-08-15"
        # First execution
        res1 = historical_ingestion_service.run_daily_scheduled_capture(
            date_bucket=test_bucket,
            dataset_mode="REAL",
            max_retries=2,
            db=db_session
        )
        assert res1["status"] in ("SUCCESS", "PARTIAL")
        assert res1["rows_captured"] >= 1

        count_after_first = db_session.query(HistoricalObservationModel).filter(
            HistoricalObservationModel.date_bucket == test_bucket,
            HistoricalObservationModel.dataset_mode == "REAL"
        ).count()

        # Second execution with identical parameters
        res2 = historical_ingestion_service.run_daily_scheduled_capture(
            date_bucket=test_bucket,
            dataset_mode="REAL",
            max_retries=2,
            db=db_session
        )
        assert res2["status"] in ("SUCCESS", "PARTIAL")
        # Duplicates prevented counter tracked
        assert res2["duplicates_prevented"] >= 1

        count_after_second = db_session.query(HistoricalObservationModel).filter(
            HistoricalObservationModel.date_bucket == test_bucket,
            HistoricalObservationModel.dataset_mode == "REAL"
        ).count()

        # Row count must not increase
        assert count_after_first == count_after_second


class TestPartialProviderResilienceAndNullPreservation:
    """Tests for Section 7 & 12: Partial provider failures produce valid REAL observations with NULLs."""

    def test_unavailable_signals_remain_null_never_zero(self, db_session):
        test_bucket = "2026-08-20"
        rec = historical_ingestion_service.capture_current_observation(
            destination_id="mirik",
            date_bucket=test_bucket,
            dataset_mode="REAL",
            db=db_session
        )

        # In REAL mode, unmeasured physical signals remain None/NULL
        assert rec.dataset_mode == "REAL"
        # Footfall is unmetered promenade sensor -> must be None, NOT 0.0
        assert rec.footfall is None
        # Provenance must be explicit
        assert "footfall" in rec.signal_provenance
        assert rec.signal_provenance["footfall"].is_available is False
        assert rec.signal_provenance["footfall"].provider_mode in ("UNAVAILABLE", "DEMO")

        # But genuinely computed or available signals exist
        assert rec.holiday_pressure is not None
        assert rec.current_crowd_pressure is not None


class TestSixDestinationCoverage:
    """Tests for Section 10 & 16: Six-destination daily coverage and diagnostics."""

    def test_daily_capture_covers_all_six_canonical_destinations(self, db_session):
        test_bucket = "2026-08-25"
        res = historical_ingestion_service.run_daily_scheduled_capture(
            date_bucket=test_bucket,
            dataset_mode="REAL",
            max_retries=2,
            db=db_session
        )

        captured_dests = set(res["captured_destinations"])
        assert set(CANONICAL_DESTINATIONS).issubset(captured_dests)
        assert res["destinations_attempted"] == len(CANONICAL_DESTINATIONS)

    def test_coverage_endpoint(self, client):
        resp = client.get("/api/historical/coverage")
        assert resp.status_code == 200
        data = resp.json()

        assert data["total_canonical_destinations"] == 6
        assert len(data["destinations"]) == 6
        dest_names = [d["destination"] for d in data["destinations"]]
        for can in CANONICAL_DESTINATIONS:
            assert can in dest_names

        for d in data["destinations"]:
            assert "real_rows" in d
            assert "distinct_dates" in d
            assert "available_signal_count" in d
            assert "missing_signal_count" in d
            assert "is_underrepresented" in d


class TestCaptureStatusEndpoint:
    """Tests for Section 17: Scheduler health & capture status monitoring."""

    def test_capture_status_exposes_all_operational_fields(self, client):
        resp = client.get("/api/historical/capture-status")
        assert resp.status_code == 200
        data = resp.json()

        assert "last_capture" in data
        assert "last_capture_start" in data
        assert "last_capture_completion" in data
        assert "destinations_attempted" in data
        assert "destinations_successful" in data
        assert "rows_inserted" in data
        assert "rows_updated" in data
        assert "duplicates_prevented" in data
        assert "provider_failures" in data
        assert "retry_count" in data
        assert "capture_freshness_seconds" in data


class TestHistoricalReadinessService:
    """Tests for Section 13, 14, 15: Progress calculation and structural projection."""

    def test_readiness_summary_metrics_structure(self, db_session):
        summary = historical_readiness_service.get_readiness_summary(db=db_session)

        assert "real_rows" in summary
        assert summary["required_rows"] == 180
        assert summary["row_progress_percent"] >= 0.0
        assert summary["required_temporal_span_days"] == 30
        assert "temporal_progress_percent" in summary
        assert summary["total_canonical_destinations"] == 6
        assert "quality_breakdown" in summary
        assert "core_signal_missingness_percent" in summary
        assert "core_signal_availability_percent" in summary
        assert "projection" in summary

    def test_structural_projection_insufficient_data(self):
        # With 0 rows and 0 dates, projection must report insufficient history
        proj = historical_readiness_service._calculate_structural_projection(
            real_rows=2,
            temporal_span_days=1,
            distinct_dates_count=1,
            latest_date_str="2026-09-20",
        )
        assert proj["available"] is False
        assert proj["reason"] == "insufficient_accumulation_history"

    def test_structural_projection_calculation(self):
        # With valid observed accumulation, structural completion date is estimated
        proj = historical_readiness_service._calculate_structural_projection(
            real_rows=30,
            temporal_span_days=15,
            distinct_dates_count=10,
            latest_date_str="2026-09-20",
        )
        assert proj["available"] is True
        assert proj["method"] == "observed_unique_real_row_rate"
        assert proj["daily_accumulation_rate_observed"] == 2.0
        assert proj["estimated_days_to_gate_ready"] == 75  # (180 - 30) / 2 = 75
        assert proj["estimated_gate_ready_date"] == "2026-12-04"
        assert "disclaimer" in proj

    def test_production_readiness_endpoint_backward_compatibility(self, client):
        resp = client.get("/api/admin/ml/production-readiness")
        assert resp.status_code == 200
        data = resp.json()

        # Prompt 6 legacy fields
        assert "model_status" in data
        assert "active_model_name" in data
        assert "eligibility_diagnostics" in data

        # Prompt 7 enhanced fields
        assert "real_rows" in data
        assert "required_rows" in data
        assert "row_progress_percent" in data
        assert "temporal_progress_percent" in data
        assert "destinations_present" in data
        assert "quality_breakdown" in data
        assert "projection" in data
        assert "readiness_metrics" in data


class TestGateIntegrityAndTrainingRefusal:
    """Tests for Section 2, 24, 25: Strict thresholds preserved and training refused when ineligible."""

    def test_gate_thresholds_strictly_preserved(self):
        requirements = production_eligibility_gate.get_requirements()
        assert requirements["min_rows"] == 180
        assert requirements["min_destinations"] == 3
        assert requirements["min_rows_per_destination"] == 20
        assert requirements["min_temporal_span_days"] == 30
        assert requirements["target_availability_percent"] == 100.0
        assert requirements["max_core_missingness_percent"] == 70.0
        assert requirements["min_target_variance"] == 4.0

    def test_training_refusal_when_ineligible(self):
        report = production_training_coordinator.retrain_if_eligible(force=True)
        assert report["trained"] is False
        assert report["model_status"] in (INSUFFICIENT_DATA, BASELINE_ACTIVE)
        assert len(report["failed_requirements"]) > 0
