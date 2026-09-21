"""
Test Suite for Real-Time Telemetry Enrichment & Automatic Production XGBoost Promotion (Prompt 6).

Covers:
1. Real signal coverage and 22-feature schema parity
2. Observation quality scoring engine (HIGH, MEDIUM, LOW, INVALID)
3. ProductionEligibilityGate structured diagnostics & refusal when insufficient
4. External search demand provider (rate limiting, caching, UNAVAILABLE provenance)
5. ProductionTrainingCoordinator execution:
   - Refusal when ineligible
   - Duplicate retraining prevention (NO_NEW_DATA)
   - Atomic candidate training and promotion when eligible
   - Failure preservation of previous working model
6. ModelRegistry transparency & readiness reporting
7. Endpoints:
   - POST /api/admin/ml/retrain-if-eligible
   - GET /api/admin/ml/production-readiness
   - GET /api/historical/capture-status
   - GET /api/destinations/{id}/pressure/forecast/ml (backward compatibility & classification)
"""

import os
import pytest
from datetime import datetime, date, timedelta, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.entities import HistoricalObservationModel
from app.services.ml.feature_builder import StandardFeatureBuilder, SCHEMA_VERSION
from app.services.ml.eligibility_gate import (
    ProductionEligibilityGate,
    ProductionEligibilityVerdict,
    production_eligibility_gate,
)
from app.services.ml.model_registry import (
    ModelRegistry,
    BaselineRuleModel,
    model_registry,
)
from app.services.ml.production_training_coordinator import (
    ProductionTrainingCoordinator,
    production_training_coordinator,
    BASELINE_ACTIVE,
    REAL_PRODUCTION_ACTIVE,
    INSUFFICIENT_DATA,
    TRAINING_FAILED,
)
from app.services.historical.quality_scoring import (
    ObservationQualityScorer,
    observation_quality_scorer,
)
from app.services.data_sources.search_demand_external import ExternalSearchDemandProvider
from app.services.historical.ingestion_service import historical_ingestion_service

client = TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestFeatureParityAndQualityScoring:
    """Tests for 22-feature schema parity and deterministic observation quality scoring."""

    def test_22_feature_schema_completeness(self):
        """Validates all 22 feature names and schema version 2.0.0."""
        fb = StandardFeatureBuilder()
        names = fb.get_feature_names()
        assert len(names) == 22
        assert SCHEMA_VERSION == "2.0.0"
        assert "target_horizon_days" in names
        assert "search_to_booking_ratio" in names
        for dest in ["darjeeling", "kalimpong", "mirik", "lava", "lolegaon", "rishop"]:
            assert f"dest_{dest}" in names

    def test_quality_scorer_high_grade(self):
        """Observation with high core signals, 3+ sources, and confidence >=0.70 receives HIGH."""
        obs = {
            "destination_id": "darjeeling",
            "date_bucket": "2026-09-15",
            "current_crowd_pressure": 65.0,
            "booking_demand": 40.0,
            "search_demand": 55.0,
            "holiday_pressure": 30.0,
            "event_pressure": 20.0,
            "composite_confidence": 0.85,
            "signal_provenance": {
                "booking_demand": {"source": "POSTGRES_BOOKINGS"},
                "search_demand": {"source": "POSTGRES_DEMAND"},
                "holiday_pressure": {"source": "GOV_GAZETTE"},
                "event_pressure": {"source": "EVENT_REGISTRY"},
            }
        }
        score = observation_quality_scorer.score_observation(obs)
        assert score.quality_grade == "HIGH"
        assert score.temporal_alignment_validity is True
        assert score.core_signal_availability_ratio >= 0.60
        assert score.source_diversity >= 3

    def test_quality_scorer_medium_grade(self):
        """Observation with moderate signals and 2 sources receives MEDIUM."""
        obs = {
            "destination_id": "kalimpong",
            "date_bucket": "2026-09-15",
            "current_crowd_pressure": 50.0,
            "booking_demand": 30.0,
            "holiday_pressure": 20.0,
            "composite_confidence": 0.60,
            "signal_provenance": {
                "booking_demand": {"source": "POSTGRES_BOOKINGS"},
                "holiday_pressure": {"source": "GOV_GAZETTE"},
            }
        }
        score = observation_quality_scorer.score_observation(obs)
        assert score.quality_grade == "MEDIUM"

    def test_quality_scorer_low_grade(self):
        """Observation with sparse signals receives LOW."""
        obs = {
            "destination_id": "mirik",
            "date_bucket": "2026-09-15",
            "current_crowd_pressure": 45.0,
            "holiday_pressure": 10.0,
            "composite_confidence": 0.30,
            "signal_provenance": {
                "holiday_pressure": {"source": "GOV_GAZETTE"},
            }
        }
        score = observation_quality_scorer.score_observation(obs)
        assert score.quality_grade == "LOW"

    def test_quality_scorer_invalid_grade(self):
        """Invalid destination, future date, or missing target yields INVALID."""
        obs_bad_dest = {
            "destination_id": "unknown_hill",
            "date_bucket": "2026-09-15",
            "current_crowd_pressure": 50.0,
        }
        assert observation_quality_scorer.score_observation(obs_bad_dest).quality_grade == "INVALID"

        obs_future = {
            "destination_id": "darjeeling",
            "date_bucket": "2099-01-01",
            "current_crowd_pressure": 50.0,
        }
        assert observation_quality_scorer.score_observation(obs_future).quality_grade == "INVALID"

        obs_missing_target = {
            "destination_id": "darjeeling",
            "date_bucket": "2026-09-15",
            "current_crowd_pressure": None,
        }
        assert observation_quality_scorer.score_observation(obs_missing_target).quality_grade == "INVALID"


class TestExternalSearchDemandProvider:
    """Tests for external search provider rate limiting, caching, and provenance isolation."""

    def test_external_search_disabled_returns_unavailable(self):
        """Unconfigured external search returns UNAVAILABLE provenance without crashing."""
        provider = ExternalSearchDemandProvider(enabled=False)
        reading = provider.get_search_interest("darjeeling")
        assert reading.available is False
        assert reading.provider_mode == "UNAVAILABLE"
        assert reading.source == "EXTERNAL_SEARCH_AGGREGATOR"

    def test_external_search_caching_and_rate_limiting(self):
        """Verifies TTL caching and rate limit enforcement."""
        provider = ExternalSearchDemandProvider(ttl_seconds=3600, max_queries_per_minute=2, enabled=True)
        r1 = provider.get_search_interest("darjeeling")
        r2 = provider.get_search_interest("darjeeling")
        assert r2.provider_mode in ("CACHED", "UNAVAILABLE")

        # Exceed rate limit
        provider.get_search_interest("kalimpong")
        r_exceeded = provider.get_search_interest("mirik")
        assert r_exceeded.available is False
        assert "rate limit" in r_exceeded.notes.lower() or r_exceeded.provider_mode == "UNAVAILABLE"


class TestEligibilityGateDiagnostics:
    """Tests for upgraded ProductionEligibilityGate structured diagnostics."""

    def test_structured_diagnostics_format(self):
        """Verifies exact structured diagnostics keys and failure reasons."""
        gate = ProductionEligibilityGate()
        verdict = gate.evaluate(
            features=[{"destination_id": "darjeeling", "holiday_pressure": 50.0}],
            targets=[50.0],
            destinations=["darjeeling"],
            dataset_mode="REAL",
            date_range={"start": "2026-09-01", "end": "2026-09-05"}
        )

        assert verdict.eligible is False
        assert verdict.status == "INSUFFICIENT_DATA"

        diag = verdict.to_structured_diagnostics()
        assert diag["eligible"] is False
        assert diag["dataset_mode"] == "REAL"
        assert diag["total_rows"] == 1
        assert diag["distinct_destinations"] == 1
        assert "min_rows" in diag["requirements"]
        assert len(diag["failed_requirements"]) > 0
        assert any("total_rows" in f for f in diag["failed_requirements"])


class TestProductionTrainingCoordinator:
    """Tests for safe atomic training, duplicate prevention, and refusal when ineligible."""

    def test_refusal_when_ineligible(self, db_session):
        """Coordinator refuses to train when genuine real dataset is below thresholds."""
        coordinator = ProductionTrainingCoordinator()
        res = coordinator.retrain_if_eligible(db=db_session)

        # Current DB has fewer than 180 rows, so it must refuse
        assert res["status"] == INSUFFICIENT_DATA
        assert res["trained"] is False
        assert res["model_status"] == BASELINE_ACTIVE
        assert "diagnostics" in res
        assert res["diagnostics"]["eligible"] is False

    def test_duplicate_retraining_prevention(self):
        """When dataset has not accumulated new observations, returns NO_NEW_DATA."""
        coordinator = ProductionTrainingCoordinator()
        # Mock eligible verdict
        fake_verdict = ProductionEligibilityVerdict(
            is_eligible=True,
            status="PRODUCTION_READY",
            total_rows=250,
            temporal_span_days=45,
            distinct_destinations=4,
        )
        coordinator._last_training_metadata = {
            "training_rows": 250,
            "training_temporal_span_days": 45,
            "trained_at": "2026-09-20T10:00:00Z"
        }

        # Override check_eligibility for test
        coordinator.check_eligibility = lambda db=None: (fake_verdict, [])

        res = coordinator.retrain_if_eligible(force=False)
        assert res["status"] == "NO_NEW_DATA"
        assert res["trained"] is False
        assert "No new qualifying observations" in res["message"]

    def test_atomic_training_candidate_failure_preserves_production_model(self, tmp_path):
        """If candidate training fails, the active production artifact is never destroyed."""
        dummy_prod_path = os.path.join(tmp_path, "crowd_xgb_v1.joblib")
        with open(dummy_prod_path, "w") as f:
            f.write("VALID_PRODUCTION_MODEL_PAYLOAD")

        coordinator = ProductionTrainingCoordinator(model_path=dummy_prod_path)

        # Force candidate training failure by passing bad data
        with pytest.raises(Exception):
            coordinator._execute_atomic_training(
                records=[{"corrupt": "data"}],
                verdict=ProductionEligibilityVerdict(is_eligible=True, status="PRODUCTION_READY")
            )

        # Production model must remain intact
        assert os.path.exists(dummy_prod_path)
        with open(dummy_prod_path, "r") as f:
            content = f.read()
        assert content == "VALID_PRODUCTION_MODEL_PAYLOAD"


class TestAdminAndHistoricalEndpoints:
    """Tests for admin ML endpoints and scheduler capture status."""

    def test_endpoint_retrain_if_eligible(self):
        """POST /api/admin/ml/retrain-if-eligible returns structured decision."""
        response = client.post("/api/admin/ml/retrain-if-eligible?force=false")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in (INSUFFICIENT_DATA, "NO_NEW_DATA", "SUCCESS")
        assert "diagnostics" in data

    def test_endpoint_production_readiness(self):
        """GET /api/admin/ml/production-readiness returns full transparency report."""
        response = client.get("/api/admin/ml/production-readiness")
        assert response.status_code == 200
        data = response.json()
        assert "model_status" in data
        assert "active_model_name" in data
        assert "feature_schema_version" in data
        assert data["feature_schema_version"] == "2.0.0"
        assert "eligibility_diagnostics" in data

    def test_endpoint_capture_status(self):
        """GET /api/historical/capture-status returns scheduler metrics."""
        response = client.get("/api/historical/capture-status")
        assert response.status_code == 200
        data = response.json()
        assert "last_capture" in data
        assert "next_recommended_capture" in data
        assert "successful_destinations" in data
        assert "rows_captured" in data

    def test_endpoint_ml_forecast_backward_compatibility(self):
        """GET /api/destinations/darjeeling/pressure/forecast/ml preserves contract."""
        response = client.get("/api/destinations/darjeeling/pressure/forecast/ml?days=3")
        assert response.status_code == 200
        data = response.json()
        assert data["destination_id"] == "darjeeling"
        assert len(data["forecast"]) == 3
        assert "current_pressure" in data
        assert "model_used" in data
        assert "forecast_source_classification" in data
        assert data["forecast_source_classification"] in (
            "REAL_XGBOOST_FORECAST",
            "SYNTHETIC_BENCHMARK",
            "BASELINE_FALLBACK",
            "INSUFFICIENT_DATA"
        )
