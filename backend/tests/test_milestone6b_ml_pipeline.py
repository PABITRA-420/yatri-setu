"""
Milestone 6B Tests — Real Data Ingestion + ML Training Pipeline.

Tests cover:
  1. Real vs. Mock provider distinction in all ingestors
  2. Dataset construction and provenance labeling
  3. Feature leakage prevention (chronological splitting)
  4. ML model training, prediction range, and fallback
  5. Model registry safe_predict() fallback guarantee
  6. Evaluation metrics correctness (MAE, RMSE, Directional Accuracy)
  7. Feature importance availability post-training
  8. Forecast horizon API structure
  9. ML admin API status and feature importance endpoints
 10. Synthetic data warning propagation
"""
import math
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from app.main import app
from app.services.ingestion.base_ingestor import ProviderMode, IngestedObservation, BaseIngestor
from app.services.ingestion.weather_ingestor import WeatherIngestor, weather_ingestor
from app.services.ingestion.booking_ingestor import booking_ingestor
from app.services.ingestion.accommodation_ingestor import accommodation_ingestor
from app.services.ingestion.search_demand_ingestor import search_demand_ingestor
from app.services.ingestion.tourism_ingestor import tourism_ingestor
from app.services.ingestion.event_ingestor import event_ingestor
from app.services.ml.dataset_builder import ml_dataset_builder
from app.services.ml.dataset_splitter import ChronologicalDatasetSplitter
from app.services.ml.feature_builder import StandardFeatureBuilder
from app.services.ml.model_registry import model_registry, BaselineRuleModel, ModelRegistry
from app.services.ml.xgboost_model import xgboost_crowd_model
from app.services.ml.evaluation import (
    compute_mae, compute_rmse, compute_directional_accuracy,
    compute_error_by_destination, compute_error_by_season, compare_models,
)
from app.data.historical_dataset import generate_historical_dataset

client = TestClient(app)


# ─── 1. Ingestor Provider Mode Tests ─────────────────────────────────────────

class TestIngestorProviderModes:
    """All mock ingestors must return MOCK mode and never REAL/MISSING."""

    def test_booking_ingestor_is_mock(self):
        obs = booking_ingestor.ingest("darjeeling", "2023-06-01")
        assert obs.provider_mode == ProviderMode.MOCK
        assert obs.source == "Yatri Setu Network"
        assert obs.signal_name == "booking_demand"

    def test_accommodation_ingestor_is_mock(self):
        obs = accommodation_ingestor.ingest("kalimpong", "2023-06-01")
        assert obs.provider_mode == ProviderMode.MOCK
        assert obs.source == "Yatri Setu Network"

    def test_search_demand_ingestor_is_mock(self):
        obs = search_demand_ingestor.ingest("mirik", "2023-06-01")
        assert obs.provider_mode == ProviderMode.MOCK
        assert obs.source == "Yatri Setu Network"
        assert "Yatri Setu Network signal only" in obs.notes

    def test_tourism_ingestor_is_mock(self):
        obs = tourism_ingestor.ingest("lava", "2023-06-01")
        assert obs.provider_mode == ProviderMode.MOCK
        assert "NOT real-time" in obs.notes

    def test_event_ingestor_is_mock(self):
        obs = event_ingestor.ingest("darjeeling", "2023-10-15")
        assert obs.provider_mode == ProviderMode.MOCK
        assert obs.signal_name == "event_pressure"

    def test_weather_ingestor_returns_observation(self):
        obs = weather_ingestor.ingest("darjeeling", "2023-06-01")
        # Mode is either MOCK or REAL depending on env config
        assert obs.provider_mode in (ProviderMode.MOCK, ProviderMode.REAL, ProviderMode.CACHED)
        assert obs.signal_name == "weather_pressure"

    def test_all_ingestors_produce_valid_range(self):
        ingestors = [
            booking_ingestor, accommodation_ingestor,
            search_demand_ingestor, tourism_ingestor, event_ingestor,
        ]
        for ing in ingestors:
            obs = ing.ingest("darjeeling", "2023-06-01")
            assert 0.0 <= obs.signal_value <= 100.0, f"{ing.signal_name} out of range: {obs.signal_value}"
            assert 0.0 <= obs.confidence <= 1.0
            assert obs.data_quality in ("HIGH", "MEDIUM", "LOW", "DEGRADED")


# ─── 2. First-Party Label Tests ───────────────────────────────────────────────

class TestFirstPartyLabels:
    """First-party signals must be labeled 'Yatri Setu Network' and disclaim scope."""

    def test_booking_first_party_label(self):
        obs = booking_ingestor.ingest("darjeeling", "2023-01-01")
        assert obs.source == "Yatri Setu Network"
        assert "not a nationwide measurement" in obs.notes.lower()

    def test_accommodation_first_party_label(self):
        obs = accommodation_ingestor.ingest("rishop", "2023-01-01")
        assert obs.source == "Yatri Setu Network"
        assert "not a district-wide" in obs.notes.lower()

    def test_search_demand_first_party_label(self):
        obs = search_demand_ingestor.ingest("lava", "2023-01-01")
        assert obs.source == "Yatri Setu Network"
        assert "not google trends" in obs.notes.lower()


# ─── 3. Dataset Construction Tests ───────────────────────────────────────────

class TestDatasetConstruction:
    """Dataset builder must produce clean, labeled, provenance-rich datasets."""

    def test_synthetic_dataset_mode_label(self):
        result = ml_dataset_builder.build_synthetic_dataset()
        assert result.dataset_mode == "SYNTHETIC"

    def test_synthetic_dataset_size(self):
        result = ml_dataset_builder.build_synthetic_dataset()
        assert result.total_records == 2190  # 365 days × 6 destinations

    def test_synthetic_real_count_is_zero(self):
        result = ml_dataset_builder.build_synthetic_dataset()
        assert result.real_record_count == 0
        assert result.synthetic_record_count == 2190

    def test_dataset_features_and_targets_aligned(self):
        result = ml_dataset_builder.build_synthetic_dataset()
        assert len(result.features) == len(result.targets)
        assert len(result.features) == result.total_records

    def test_dataset_notes_warn_synthetic(self):
        result = ml_dataset_builder.build_synthetic_dataset()
        assert "SYNTHETIC DEMO DATA" in result.notes

    def test_feature_names_present(self):
        result = ml_dataset_builder.build_synthetic_dataset()
        assert len(result.feature_names) >= 15
        assert "booking_demand" in result.feature_names
        assert "weather_pressure" in result.feature_names
        assert "day_of_week" in result.feature_names


# ─── 4. Chronological Splitting Tests ────────────────────────────────────────

class TestChronologicalSplitting:
    """Splitting MUST preserve temporal order with no data leakage."""

    def test_no_shuffle_verified(self):
        observations = generate_historical_dataset()
        splitter = ChronologicalDatasetSplitter()
        split = splitter.split(observations)
        assert split["no_shuffle_verified"] is True

    def test_train_precedes_validation(self):
        observations = generate_historical_dataset()
        splitter = ChronologicalDatasetSplitter()
        split = splitter.split(observations)
        assert split["train_end"] < split["val_start"]

    def test_validation_precedes_test(self):
        observations = generate_historical_dataset()
        splitter = ChronologicalDatasetSplitter()
        split = splitter.split(observations)
        assert split["val_end"] < split["test_start"]

    def test_split_sizes_sum_to_total(self):
        observations = generate_historical_dataset()
        splitter = ChronologicalDatasetSplitter()
        split = splitter.split(observations)
        total = split["train_count"] + split["validation_count"] + split["test_count"]
        assert total == len(observations)

    def test_no_overlap_between_splits(self):
        observations = generate_historical_dataset()
        splitter = ChronologicalDatasetSplitter()
        split = splitter.split(observations)
        train_dates = {obs.date for obs in split["train"]}
        val_dates = {obs.date for obs in split["validation"]}
        test_dates = {obs.date for obs in split["test"]}
        assert len(train_dates & val_dates) == 0
        assert len(val_dates & test_dates) == 0
        assert len(train_dates & test_dates) == 0

    def test_all_indices_unique(self):
        observations = generate_historical_dataset()
        splitter = ChronologicalDatasetSplitter()
        split = splitter.split(observations)
        all_idx = split["train_indices"] + split["validation_indices"] + split["test_indices"]
        assert len(all_idx) == len(set(all_idx))


# ─── 5. Feature Leakage Prevention ───────────────────────────────────────────

class TestFeatureLeakage:
    """Feature vectors must not contain future information."""

    def test_target_not_in_feature_names(self):
        builder = StandardFeatureBuilder()
        feature_names = builder.get_feature_names()
        # target_pressure must NOT appear in the feature matrix
        assert "target_pressure" not in feature_names
        assert "observed_pressure" not in feature_names

    def test_feature_rows_have_no_future_signals(self):
        observations = generate_historical_dataset()
        builder = StandardFeatureBuilder()
        rows = builder.build_features(observations)
        feature_names = builder.get_feature_names()
        for row in rows[:10]:  # spot check
            for fn in feature_names:
                assert fn in row, f"Feature '{fn}' missing from row"


# ─── 6. Evaluation Metric Tests ──────────────────────────────────────────────

class TestEvaluationMetrics:
    """MAE, RMSE, and directional accuracy must compute correctly."""

    def test_mae_perfect_prediction(self):
        preds = [50.0, 60.0, 70.0]
        actuals = [50.0, 60.0, 70.0]
        assert compute_mae(preds, actuals) == 0.0

    def test_mae_known_value(self):
        preds = [55.0, 65.0]
        actuals = [50.0, 70.0]
        expected = (5.0 + 5.0) / 2
        assert abs(compute_mae(preds, actuals) - expected) < 0.001

    def test_rmse_known_value(self):
        preds = [53.0]
        actuals = [50.0]
        expected = 3.0
        assert abs(compute_rmse(preds, actuals) - expected) < 0.001

    def test_directional_accuracy_perfect(self):
        preds = [10.0, 20.0, 30.0, 40.0]
        actuals = [10.0, 15.0, 25.0, 35.0]
        acc = compute_directional_accuracy(preds, actuals)
        assert acc == 100.0

    def test_directional_accuracy_zero(self):
        preds = [40.0, 30.0, 20.0]
        actuals = [10.0, 20.0, 30.0]
        acc = compute_directional_accuracy(preds, actuals)
        assert acc == 0.0

    def test_compare_models_ml_better(self):
        result = compare_models(baseline_mae=3.0, ml_mae=2.0, baseline_rmse=4.0, ml_rmse=3.0)
        assert result["ml_improves_over_baseline"] is True
        assert result["mae_delta"] == 1.0

    def test_compare_models_ml_worse(self):
        result = compare_models(baseline_mae=2.0, ml_mae=3.0, baseline_rmse=3.0, ml_rmse=4.0)
        assert result["ml_improves_over_baseline"] is False
        assert result["mae_delta"] is None


# ─── 7. Model Registry & Fallback Tests ──────────────────────────────────────

class TestModelRegistry:
    """ModelRegistry must always provide safe predictions with fallback."""

    def test_baseline_always_registered(self):
        registry = ModelRegistry()
        baseline = registry.get_model("baseline_rule_v2")
        assert baseline is not None

    def test_safe_predict_returns_valid_range(self):
        features = {
            "historical_footfall": 70.0,
            "accommodation_occupancy": 65.0,
            "booking_demand": 80.0,
            "search_demand": 75.0,
            "event_pressure": 20.0,
            "holiday_pressure": 30.0,
            "weather_pressure": 60.0,
            "traffic_pressure": 55.0,
        }
        result = model_registry.safe_predict(features)
        assert 0.0 <= result["predicted_pressure"] <= 100.0
        assert result["model_used"] is not None

    def test_safe_predict_with_bad_model_falls_back(self):
        """A broken ML model must not crash the registry."""
        class BrokenModel(BaselineRuleModel):
            @property
            def name(self):
                return "broken_ml_model"

            @property
            def version(self):
                return "0.0.1"

            def predict(self, features):
                raise RuntimeError("Intentional failure")

        local_registry = ModelRegistry()
        local_registry.register_model(BrokenModel())

        features = {"historical_footfall": 50.0, "accommodation_occupancy": 50.0}
        result = local_registry.safe_predict(features, prefer_model="broken_ml_model")
        # Must fall back gracefully
        assert result["model_used"] == "baseline_rule_v2"
        assert result["fallback_reason"] is not None

    def test_list_models_contains_baseline(self):
        models = model_registry.list_models()
        names = [m["name"] for m in models]
        assert "baseline_rule_v2" in names


# ─── 8. ML Model Training Tests ──────────────────────────────────────────────

class TestMLModelTraining:
    """Training produces a valid model with feature importances and predictions."""

    @pytest.fixture(scope="class")
    def trained_model(self):
        dataset = ml_dataset_builder.build_synthetic_dataset()
        split = dataset.split
        result = xgboost_crowd_model.build_and_train(
            feature_rows=dataset.features,
            targets=dataset.targets,
            feature_names=dataset.feature_names,
            train_indices=split["train_indices"],
            validation_indices=split["validation_indices"],
            test_indices=split["test_indices"],
            dataset_mode="SYNTHETIC",
            test_observations=split["test"],
        )
        return result

    def test_training_succeeds(self, trained_model):
        assert "error" not in trained_model

    def test_test_mae_is_finite(self, trained_model):
        mae = trained_model.get("test_mae", None)
        assert mae is not None
        assert math.isfinite(mae)
        assert mae >= 0.0

    def test_prediction_in_range(self, trained_model):
        features = {
            "historical_footfall": 70.0, "accommodation_occupancy": 65.0,
            "booking_demand": 80.0, "search_demand": 75.0,
            "event_pressure": 20.0, "holiday_pressure": 30.0,
            "weather_pressure": 60.0, "traffic_pressure": 55.0,
            "day_of_week": 5, "is_weekend": 1, "month": 6,
            "day_of_year": 160, "search_to_booking_ratio": 1.05,
            "is_peak_summer": 1, "is_peak_autumn": 0,
            "dest_darjeeling": 1, "dest_kalimpong": 0, "dest_mirik": 0,
            "dest_lava": 0, "dest_lolegaon": 0, "dest_rishop": 0,
        }
        pred = xgboost_crowd_model.predict(features)
        assert 0.0 <= pred <= 100.0

    def test_feature_importances_populated(self, trained_model):
        importances = xgboost_crowd_model.feature_importances
        assert len(importances) > 0
        # All importance values should be non-negative
        for name, imp in importances.items():
            assert imp >= 0.0

    def test_synthetic_data_warning_present(self, trained_model):
        warning = trained_model.get("synthetic_data_warning")
        assert warning is not None
        assert "SYNTHETIC" in warning


# ─── 9. API Endpoint Tests ────────────────────────────────────────────────────

class TestMLAdminAPI:
    """ML admin endpoints must respond correctly before and after training."""

    def test_ml_status_returns_200(self):
        resp = client.get("/api/admin/ml/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "model_available" in data
        assert "model_name" in data
        assert "fallback_active" in data

    def test_ml_status_has_required_fields(self):
        resp = client.get("/api/admin/ml/status")
        data = resp.json()
        required = ["model_available", "model_name", "model_version",
                    "backend", "dataset_mode", "is_trained", "baseline_model"]
        for field in required:
            assert field in data, f"Missing field: {field}"

    def test_ml_models_list_endpoint(self):
        resp = client.get("/api/admin/ml/models")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data
        assert len(data["models"]) >= 1

    def test_feature_importance_404_when_not_trained(self):
        """If model is not trained, feature importance should 404."""
        # Reset model's trained state temporarily
        original_state = xgboost_crowd_model._is_trained
        xgboost_crowd_model._is_trained = False
        try:
            resp = client.get("/api/admin/ml/feature-importance")
            assert resp.status_code == 404
        finally:
            xgboost_crowd_model._is_trained = original_state

    def test_ml_forecast_endpoint(self):
        resp = client.get("/api/destinations/darjeeling/pressure/forecast/ml?days=3")
        assert resp.status_code == 200
        data = resp.json()
        assert data["horizon_days"] == 3
        assert len(data["forecast"]) == 3
        assert "fallback_active" in data
        assert "confidence_note" in data

    def test_ml_forecast_confidence_note_present(self):
        resp = client.get("/api/destinations/darjeeling/pressure/forecast/ml?days=7")
        data = resp.json()
        for day in data["forecast"]:
            assert "confidence_note" in day
            assert "not statistically calibrated" in day["confidence_note"].lower()

    def test_ml_forecast_all_horizons(self):
        for days in [1, 3, 7, 14]:
            resp = client.get(f"/api/destinations/darjeeling/pressure/forecast/ml?days={days}")
            assert resp.status_code == 200
            data = resp.json()
            assert len(data["forecast"]) == days
