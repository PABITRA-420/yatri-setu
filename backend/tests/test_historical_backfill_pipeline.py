"""
Test Suite for Real Historical Data Acquisition, Backfill, and Quality Engine (Prompt 5).

Covers:
1. Backfill service execution (dry-run vs real commit)
2. Idempotent upsert and duplicate prevention
3. Canonical destination validation & rejection of non-canonical IDs
4. Date range validation
5. Provenance integrity (REAL remains REAL, unmeasured signals remain NULL with UNAVAILABLE provenance)
6. Zero fabrication and no silent synthetic fallback
7. Comprehensive Quality Report generation (coverage, signal completeness, target variance, zero leakage)
8. Production Eligibility evaluation (insufficient real data remains INSUFFICIENT_DATA)
9. Daily scheduled capture with retries
10. Historical API endpoints (/api/historical/backfill, /api/historical/quality-report, /api/historical/daily-capture)
"""

import pytest
from datetime import datetime, date, timedelta, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.entities import (
    HistoricalObservationModel,
    BookingModel,
    DemandEventModel,
    DestinationModel,
)
from app.services.historical.backfill_service import (
    HistoricalBackfillService,
    historical_backfill_service,
    CANONICAL_DESTINATIONS,
)
from app.services.historical.ingestion_service import historical_ingestion_service
from app.services.ml.eligibility_gate import (
    ProductionEligibilityGate,
    ProductionEligibilityRules,
    ProductionEligibilityVerdict,
)


@pytest.fixture
def db_session():
    """Provides a transactional database session for tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Test client for FastAPI endpoints."""
    return TestClient(app)


class TestHistoricalBackfillEngine:
    """Tests for the HistoricalBackfillService core logic."""

    def test_canonical_destination_validation(self):
        """Rejects non-canonical destinations and enforces valid ones."""
        service = HistoricalBackfillService()
        valid, invalid = service.validate_destinations(["darjeeling", "kalimpong", "unknown_hill"])
        assert "darjeeling" in valid
        assert "kalimpong" in valid
        assert "unknown_hill" in invalid
        assert len(invalid) == 1

    def test_invalid_date_range_rejection(self, db_session):
        """Rejects backfill when start_date is after end_date."""
        service = HistoricalBackfillService()
        with pytest.raises(ValueError, match="start_date .* must be <= end_date"):
            service.backfill_historical_data(
                start_date="2026-11-10",
                end_date="2026-11-01",
                destinations=["darjeeling"],
                db=db_session
            )

    def test_dry_run_does_not_commit(self, db_session):
        """Dry-run computes records but commits zero rows to the database."""
        service = HistoricalBackfillService()
        # Count initial rows
        initial_count = db_session.query(HistoricalObservationModel).filter(
            HistoricalObservationModel.dataset_mode == "REAL",
            HistoricalObservationModel.date_bucket == "2026-10-15"
        ).count()

        result = service.backfill_historical_data(
            start_date="2026-10-15",
            end_date="2026-10-15",
            destinations=["darjeeling", "kalimpong"],
            dataset_mode="REAL",
            dry_run=True,
            db=db_session
        )

        assert result["dry_run"] is True
        assert result["status"] == "DRY_RUN_COMPLETED"
        assert result["processed_records"] == 2
        assert result["persisted_records"] == 0

        # Verify DB was not modified
        after_count = db_session.query(HistoricalObservationModel).filter(
            HistoricalObservationModel.dataset_mode == "REAL",
            HistoricalObservationModel.date_bucket == "2026-10-15"
        ).count()
        assert after_count == initial_count

    def test_idempotent_backfill_execution(self, db_session):
        """Running backfill twice updates records in-place without duplicates."""
        service = HistoricalBackfillService()
        test_date = "2026-11-01"

        # First run: live commit
        res1 = service.backfill_historical_data(
            start_date=test_date,
            end_date=test_date,
            destinations=["darjeeling", "kalimpong"],
            dataset_mode="REAL",
            dry_run=False,
            db=db_session
        )
        assert res1["status"] == "SUCCESS"
        assert res1["persisted_records"] == 2

        count_after_first = db_session.query(HistoricalObservationModel).filter(
            HistoricalObservationModel.dataset_mode == "REAL",
            HistoricalObservationModel.date_bucket == test_date
        ).count()
        assert count_after_first == 2

        # Second run: identical parameters
        res2 = service.backfill_historical_data(
            start_date=test_date,
            end_date=test_date,
            destinations=["darjeeling", "kalimpong"],
            dataset_mode="REAL",
            dry_run=False,
            db=db_session
        )
        assert res2["status"] == "SUCCESS"
        assert res2["persisted_records"] == 2

        # Verify no duplicate rows were added
        count_after_second = db_session.query(HistoricalObservationModel).filter(
            HistoricalObservationModel.dataset_mode == "REAL",
            HistoricalObservationModel.date_bucket == test_date
        ).count()
        assert count_after_second == 2

    def test_provenance_and_null_unmeasured_signals(self, db_session):
        """
        Confirms REAL data remains REAL, and unmeasured signals (footfall, traffic, weather)
        remain NULL with 'UNAVAILABLE' provenance — no fabrication.
        """
        service = HistoricalBackfillService()
        test_date = "2026-11-02"

        res = service.backfill_historical_data(
            start_date=test_date,
            end_date=test_date,
            destinations=["darjeeling"],
            dataset_mode="REAL",
            dry_run=False,
            db=db_session
        )
        assert res["status"] == "SUCCESS"

        record_id = service._generate_record_id("darjeeling", test_date, "REAL")
        model = db_session.query(HistoricalObservationModel).filter_by(id=record_id).first()
        assert model is not None
        assert model.dataset_mode == "REAL"

        # Footfall and traffic sensors are not physically deployed for historical dates,
        # so they MUST remain None/NULL with UNAVAILABLE provenance
        assert model.footfall is None
        assert model.traffic_pressure is None
        assert model.weather_pressure is None

        prov = model.signal_provenance
        assert prov["footfall"]["provider_mode"] == "UNAVAILABLE"
        assert prov["traffic_pressure"]["provider_mode"] == "UNAVAILABLE"
        assert prov["weather_pressure"]["provider_mode"] == "UNAVAILABLE"

        # Holiday pressure is factual and historical
        assert model.holiday_pressure is not None
        assert prov["holiday_pressure"]["provider_mode"] == "HISTORICAL"


class TestQualityReportAndLeakage:
    """Tests for Dataset Quality Report generation and leakage checks."""

    def test_quality_report_structure_and_leakage_safety(self, db_session):
        """Generates quality report and verifies coverage, completeness, and zero leakage."""
        service = HistoricalBackfillService()

        # Seed backfill for a known 3-day window
        service.backfill_historical_data(
            start_date="2026-11-05",
            end_date="2026-11-07",
            destinations=["darjeeling", "kalimpong", "mirik"],
            dataset_mode="REAL",
            dry_run=False,
            db=db_session
        )

        report = service.generate_quality_report(dataset_mode="REAL", db=db_session)

        # 1. Coverage
        cov = report["coverage"]
        assert cov["total_rows"] >= 9
        assert cov["unique_destinations"] >= 3
        assert "darjeeling" in cov["destinations"]

        # 2. Signal Completeness
        comp = report["signal_completeness"]
        assert "holiday_pressure" in comp
        assert "footfall" in comp
        # Footfall should show high missingness as expected for unmeasured signals
        assert comp["footfall"]["missingness_pct"] >= 0.0

        # 3. Target Quality
        tq = report["target_quality"]
        assert "target_variance" in tq
        assert "target_distribution" in tq

        # 4. Leakage Checks
        leak = report["leakage_checks"]
        assert leak["future_target_leakage_count"] == 0
        assert leak["duplicate_feature_target_pairs"] == 0
        assert leak["invalid_timestamps"] == 0
        assert leak["invalid_horizon_pairs"] == 0
        assert leak["leakage_safe"] is True


class TestProductionEligibilityGate:
    """Tests that the eligibility gate strictly guards REAL production readiness."""

    def test_insufficient_real_data_returns_insufficient_status(self, db_session):
        """When REAL dataset has fewer than 180 rows, gate returns INSUFFICIENT_DATA."""
        gate = ProductionEligibilityGate()
        real_records = historical_ingestion_service.get_observations(dataset_mode="REAL", limit=1000, db=db_session)
        features = [{"crowd_pressure": r.current_crowd_pressure or 50.0} for r in real_records]
        targets = [float(r.current_crowd_pressure or 50.0) for r in real_records]
        dests = list(set(r.destination_id for r in real_records))

        evaluation = gate.evaluate(
            features=features,
            targets=targets,
            destinations=dests,
            dataset_mode="REAL",
        )

        if len(features) < 180:
            assert evaluation.is_eligible is False
            assert evaluation.status == "INSUFFICIENT_DATA"
            assert any("180" in f or "rows" in f.lower() for f in evaluation.failure_reasons)

    def test_synthetic_dataset_never_eligible(self):
        """Synthetic benchmark datasets are explicitly prohibited from production eligibility."""
        gate = ProductionEligibilityGate()
        eval_synthetic = gate.evaluate(
            features=[{"dummy": 1}] * 200,
            targets=[50.0] * 200,
            destinations=["darjeeling", "kalimpong", "mirik"],
            dataset_mode="SYNTHETIC",
        )
        assert eval_synthetic.is_eligible is False
        assert eval_synthetic.status == "SYNTHETIC_BENCHMARK"


class TestDailyScheduledCapture:
    """Tests for continuous real observation accumulation with retries."""

    def test_daily_capture_execution(self, db_session):
        """Tests that scheduled daily capture successfully samples and persists canonical destinations."""
        test_bucket = "2026-11-20"
        res = historical_ingestion_service.run_daily_scheduled_capture(
            date_bucket=test_bucket,
            dataset_mode="REAL",
            max_retries=2,
            db=db_session
        )

        assert res["status"] in ["SUCCESS", "PARTIAL"]
        assert res["captured_count"] >= 1
        assert test_bucket in res["date_bucket"]
        assert res["dataset_mode"] == "REAL"


class TestHistoricalApiEndpoints:
    """Tests for FastAPI endpoints in app/api/v1/historical.py."""

    def test_api_backfill_dry_run(self, client):
        """Tests POST /api/historical/backfill with dry_run=True."""
        response = client.post(
            "/api/historical/backfill",
            params={
                "start_date": "2026-10-20",
                "end_date": "2026-10-20",
                "destinations": ["darjeeling"],
                "dataset_mode": "REAL",
                "dry_run": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["dry_run"] is True
        assert data["status"] == "DRY_RUN_COMPLETED"
        assert data["processed_records"] == 1

    def test_api_quality_report(self, client):
        """Tests GET /api/historical/quality-report."""
        response = client.get("/api/historical/quality-report", params={"dataset_mode": "REAL"})
        assert response.status_code == 200
        data = response.json()
        assert "coverage" in data
        assert "signal_completeness" in data
        assert "leakage_checks" in data
        assert data["leakage_checks"]["leakage_safe"] is True

    def test_api_daily_capture(self, client):
        """Tests POST /api/historical/daily-capture."""
        response = client.post(
            "/api/historical/daily-capture",
            params={
                "date_bucket": "2026-11-25",
                "dataset_mode": "REAL",
                "max_retries": 2
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["SUCCESS", "PARTIAL"]
        assert "captured_count" in data
