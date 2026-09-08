"""
Test Suite for Milestone 6A: Historical Crowd Dataset + Baseline Evaluation.
Verifies deterministic dataset generation, data quality checks, chronological splitting,
error calculations (MAE/RMSE/Directional Accuracy), ML foundation interfaces, and admin APIs.
"""

import os
import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.data.historical_dataset import (
    generate_historical_dataset,
    get_historical_dataset,
    export_dataset_to_csv,
    DESTINATIONS
)
from app.models.dataset_evaluation import HistoricalObservation
from app.services.data_quality_service import data_quality_service
from app.services.baseline_evaluation import baseline_evaluation_service
from app.services.ml.feature_builder import StandardFeatureBuilder
from app.services.ml.dataset_splitter import ChronologicalDatasetSplitter
from app.services.ml.model_registry import model_registry, BaselineRuleModel

client = TestClient(app)


# 1. Dataset Generation & Determinism Tests
def test_dataset_generation_count_and_destinations():
    """Verify dataset generates 365 days across all 6 destinations (2,190 records)."""
    dataset = generate_historical_dataset(seed=42)
    assert len(dataset) == 2190 # 365 days * 6 destinations

    dest_counts = {}
    for obs in dataset:
        dest_counts[obs.destination_id] = dest_counts.get(obs.destination_id, 0) + 1

    assert len(dest_counts) == 6
    for dest in DESTINATIONS:
        assert dest_counts[dest] == 365


def test_dataset_generation_deterministic_seed():
    """Verify identical random seed produces bit-for-bit identical dataset."""
    dataset_1 = generate_historical_dataset(seed=42)
    dataset_2 = generate_historical_dataset(seed=42)

    assert len(dataset_1) == len(dataset_2)
    for o1, o2 in zip(dataset_1, dataset_2):
        assert o1.date == o2.date
        assert o1.destination_id == o2.destination_id
        assert o1.historical_footfall == o2.historical_footfall
        assert o1.observed_pressure == o2.observed_pressure
        assert o1.source == "SYNTHETIC_GENERATOR"


def test_dataset_signals_bounded():
    """Verify all 8 intelligence signals and observed pressure are bounded in [0.0, 100.0]."""
    dataset = get_historical_dataset()
    for obs in dataset:
        assert 0.0 <= obs.historical_footfall <= 100.0
        assert 0.0 <= obs.accommodation_occupancy <= 100.0
        assert 0.0 <= obs.booking_demand <= 100.0
        assert 0.0 <= obs.search_demand <= 100.0
        assert 0.0 <= obs.event_pressure <= 100.0
        assert 0.0 <= obs.holiday_pressure <= 100.0
        assert 0.0 <= obs.weather_pressure <= 100.0
        assert 0.0 <= obs.traffic_pressure <= 100.0
        assert 0.0 <= obs.observed_pressure <= 100.0


# 2. Data Quality Service Tests
def test_data_quality_service_clean_dataset():
    """Verify clean dataset passes all 6 quality checks with HIGH rating."""
    report = data_quality_service.validate_dataset()
    assert report.total_records == 2190
    assert report.destinations_count == 6
    assert report.is_valid is True
    assert report.quality_rating == "HIGH"
    assert report.completeness_score == 100.0
    assert len(report.checks) == 6
    for check in report.checks:
        assert check.passed is True
        assert check.anomalies_detected == 0


def test_data_quality_detects_duplicate():
    """Verify quality pipeline detects and flags duplicate (destination_id, date) records."""
    clean_sample = get_historical_dataset()[:10]
    # Create duplicate
    dup_obs = clean_sample[0].model_copy()
    tampered_dataset = list(clean_sample) + [dup_obs]

    report = data_quality_service.validate_dataset(tampered_dataset)
    dup_check = next(c for c in report.checks if c.name == "duplicate_records_audit")
    assert dup_check.passed is False
    assert dup_check.anomalies_detected == 1


def test_data_quality_detects_range_violation():
    """Verify quality pipeline catches signal values exceeding boundary constraints."""
    clean_sample = [obs.model_copy() for obs in get_historical_dataset()[:10]]
    # Violate range on purpose
    clean_sample[0].traffic_pressure = 105.0

    report = data_quality_service.validate_dataset(clean_sample)
    range_check = next(c for c in report.checks if c.name == "signal_range_audit")
    assert range_check.passed is False
    assert range_check.anomalies_detected == 1


# 3. Chronological Time-Series Splitting Tests (No Leakage)
def test_chronological_splitting():
    """Verify splitter enforces strict time boundaries without date overlap or leakage."""
    splitter = ChronologicalDatasetSplitter(
        train_end_date="2023-08-31",
        val_end_date="2023-10-31"
    )
    dataset = get_historical_dataset()
    splits = splitter.split(dataset)

    train_set = splits["train"]
    val_set = splits["validation"]
    test_set = splits["test"]

    assert len(train_set) + len(val_set) + len(test_set) == len(dataset)
    assert len(train_set) == 1458 # 243 days * 6
    assert len(val_set) == 366   # 61 days * 6
    assert len(test_set) == 366  # 61 days * 6

    # Test strictly monotonic time boundary: max(train) < min(val) and max(val) < min(test)
    max_train_date = max(obs.date for obs in train_set)
    min_val_date = min(obs.date for obs in val_set)
    max_val_date = max(obs.date for obs in val_set)
    min_test_date = min(obs.date for obs in test_set)

    assert max_train_date <= "2023-08-31"
    assert min_val_date >= "2023-09-01"
    assert max_val_date <= "2023-10-31"
    assert min_test_date >= "2023-11-01"


# 4. Baseline Evaluation Calculations Tests
def test_baseline_evaluation_metrics():
    """Verify MAE, RMSE, and Directional Accuracy calculations on baseline model."""
    report = baseline_evaluation_service.evaluate_baseline()

    assert report.dataset_size == 2190
    assert report.dataset_mode == "SYNTHETIC DEMO"
    assert report.overall_mae > 0.0
    assert report.overall_rmse > report.overall_mae # By definition RMSE >= MAE
    assert 75.0 <= report.directional_accuracy <= 98.0

    # Verify split metrics
    assert len(report.split_metrics) == 3
    for s in report.split_metrics:
        assert s.sample_count > 0
        assert s.mae > 0.0
        assert s.rmse > 0.0

    # Verify destination metrics
    assert len(report.error_by_destination) == 6
    for d in report.error_by_destination:
        assert d.destination_id in DESTINATIONS
        assert d.sample_count == 365
        assert d.mae > 0.0

    # Verify season metrics
    assert len(report.error_by_season) == 4
    for szn in report.error_by_season:
        assert szn.sample_count > 0
        assert szn.mae > 0.0

    # Verify data sufficiency verdict
    assert report.data_sufficiency_verdict.is_sufficient is True
    assert report.data_sufficiency_verdict.sample_size_adequate is True


# 5. ML Foundation Interfaces Tests
def test_ml_feature_builder_and_model_registry():
    """Verify feature builder extracts features and model registry holds baseline model."""
    dataset = get_historical_dataset()[:10]
    builder = StandardFeatureBuilder()
    features = builder.build_features(dataset)

    assert len(features) == 10
    first_row = features[0]
    assert "target_pressure" in first_row
    assert "is_weekend" in first_row
    assert "day_of_week" in first_row
    assert "dest_darjeeling" in first_row

    # Test ModelRegistry
    model = model_registry.get_model("baseline_rule_v2")
    assert model is not None
    assert isinstance(model, BaselineRuleModel)

    pred = model.predict(first_row)
    assert 0.0 <= pred <= 100.0


# 6. CSV Export Verification Test
def test_csv_export_file():
    """Verify CSV export writes formatted table with correct headers."""
    test_csv_path = "backend/app/data/test_crowd_export.csv"
    try:
        sample = get_historical_dataset()[:20]
        saved_path = export_dataset_to_csv(test_csv_path, sample)
        assert os.path.exists(saved_path)

        with open(saved_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 21 # 1 header + 20 data rows
            assert "historical_footfall" in lines[0]
            assert "SYNTHETIC_GENERATOR" in lines[1]
    finally:
        if os.path.exists(test_csv_path):
            os.remove(test_csv_path)


# 7. Admin API Endpoints Tests
def test_api_dataset_quality_endpoint():
    """Verify GET /api/admin/dataset/quality returns structured inspection report."""
    response = client.get("/api/admin/dataset/quality")
    assert response.status_code == 200
    data = response.json()

    assert data["dataset_mode"] == "SYNTHETIC DEMO"
    assert data["total_records"] == 2190
    assert data["destinations_count"] == 6
    assert data["quality_rating"] == "HIGH"
    assert data["is_valid"] is True
    assert len(data["checks"]) == 6


def test_api_baseline_evaluation_endpoint():
    """Verify GET /api/admin/forecast-performance/baseline returns benchmark report."""
    response = client.get("/api/admin/forecast-performance/baseline")
    assert response.status_code == 200
    data = response.json()

    assert data["dataset_size"] == 2190
    assert data["dataset_mode"] == "SYNTHETIC DEMO"
    assert "overall_mae" in data
    assert "overall_rmse" in data
    assert "directional_accuracy" in data
    assert len(data["split_metrics"]) == 3
    assert len(data["error_by_destination"]) == 6
    assert len(data["error_by_season"]) == 4
    assert data["data_sufficiency_verdict"]["is_sufficient"] is True
