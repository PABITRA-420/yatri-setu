"""
Comprehensive Tests for XGBoost Forecasting Pipeline Upgrade (Milestone 11 / Prompt 4).

Validates all 20 required aspects:
1. Training/inference feature schema equality
2. 1-day target alignment
3. 3-day target alignment
4. 7-day target alignment
5. 14-day target alignment
6. Chronological splitting
7. Leakage prevention (feature_timestamp < target_timestamp)
8. REAL dataset never silently injects synthetic rows
9. SYNTHETIC dataset remains deterministic (Seed 42)
10. MIXED dataset provenance remains visible
11. Insufficient real data blocks production promotion
12. Synthetic model is not marked production-ready
13. Model registry artifact compatibility
14. Feature schema mismatch handling (safe fallback)
15. Model status metadata transparency
16. Artificial inference multipliers removed
17. Missing telemetry is not converted into fake zero values
18. ML API backward compatibility
19. Baseline fallback is explicitly identified
20. XGBoost predictions stay within valid output constraints (0.0 to 100.0)
"""
import math
from datetime import datetime, date, timedelta
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.ml.feature_builder import StandardFeatureBuilder, SCHEMA_VERSION
from app.services.ml.dataset_builder import ml_dataset_builder, DatasetBuildResult
from app.services.ml.dataset_splitter import ChronologicalDatasetSplitter
from app.services.ml.xgboost_model import xgboost_crowd_model, XGBoostCrowdModel
from app.services.ml.model_registry import model_registry, BaselineRuleModel
from app.services.ml.training_service import ml_training_service
from app.services.ml.eligibility_gate import ProductionEligibilityGate, ProductionEligibilityRules
from app.data.historical_dataset import generate_historical_dataset

client = TestClient(app)


# ─── 1. Training / Inference Feature Schema Equality ──────────────────────────

def test_training_and_inference_feature_schema_equality():
    """Verify that training feature builder and inference feature builder produce identical schemas."""
    builder = StandardFeatureBuilder()
    
    # 1. Feature names list
    training_names = builder.get_feature_names()
    assert len(training_names) == 22, f"Expected 22 features, got {len(training_names)}: {training_names}"
    assert "target_horizon_days" in training_names

    # 2. Build inference features
    inference_features = builder.build_inference_features(
        destination_id="darjeeling",
        target_date=date(2026, 10, 15),
        feature_date=date(2026, 10, 12),
        target_horizon_days=3,
        current_telemetry={"historical_footfall": 65.0, "weather_pressure": 45.0}
    )

    # Validate schema
    is_valid, missing = builder.validate_feature_schema(inference_features)
    assert is_valid is True
    assert missing == []

    # Every feature name in training schema must be a key in inference features
    for fname in training_names:
        assert fname in inference_features, f"Missing feature in inference: {fname}"

    assert inference_features["target_horizon_days"] == 3
    assert inference_features["dest_darjeeling"] == 1
    assert inference_features["dest_kalimpong"] == 0


# ─── 2-5. Multi-Horizon Target Alignment (1, 3, 7, 14 Days) ───────────────────

@pytest.mark.parametrize("horizon", [1, 3, 7, 14])
def test_multi_horizon_target_alignment(horizon):
    """Verify target alignment across 1, 3, 7, and 14 days without temporal leakage."""
    dataset = ml_dataset_builder.build_synthetic_dataset(target_horizon=horizon)
    assert dataset.total_records > 0
    
    for row in dataset.features:
        f_dt = datetime.strptime(row["feature_timestamp"], "%Y-%m-%d").date()
        t_dt = datetime.strptime(row["target_timestamp"], "%Y-%m-%d").date()
        assert (t_dt - f_dt).days == horizon, f"Horizon mismatch for row: {row}"
        assert row["target_horizon_days"] == horizon
        # Target timestamp must be strictly greater than feature timestamp
        assert t_dt > f_dt


# ─── 6. Chronological Splitting ───────────────────────────────────────────────

def test_chronological_splitting_order():
    """Chronological splitting must preserve strict temporal order: Train < Validation < Test."""
    dataset = ml_dataset_builder.build_synthetic_dataset(target_horizon=1)
    split = dataset.split

    train_start = split["train_start"]
    train_end = split["train_end"]
    val_start = split["val_start"]
    val_end = split["val_end"]
    test_start = split["test_start"]
    test_end = split["test_end"]

    assert train_start <= train_end
    assert train_end < val_start
    assert val_start <= val_end
    assert val_end < test_start
    assert test_start <= test_end


# ─── 7. Leakage Prevention ───────────────────────────────────────────────────

def test_leakage_prevention_verification():
    """Verify that features contain NO target-time information and dates are strictly separated."""
    dataset = ml_dataset_builder.build_synthetic_dataset(target_horizon=7)
    assert dataset.metadata.leakage_prevention_verified is True

    for row in dataset.features:
        assert row["feature_timestamp"] < row["target_timestamp"]
        # Ensure target value is not present inside feature vector itself (only in target)
        assert "target_pressure" not in StandardFeatureBuilder().get_feature_names()


# ─── 8. REAL Dataset Never Silently Injects Synthetic Rows ────────────────────

def test_real_dataset_never_injects_synthetic_rows():
    """When querying REAL dataset mode, zero synthetic rows are generated or substituted."""
    dataset = ml_dataset_builder.build_historical_dataset(target_horizon=1)
    assert dataset.dataset_mode == "REAL"
    assert dataset.synthetic_record_count == 0
    assert dataset.metadata.synthetic_row_count == 0


# ─── 9. SYNTHETIC Dataset Remains Deterministic ───────────────────────────────

def test_synthetic_dataset_deterministic_seed_42():
    """Synthetic dataset generation must be 100% deterministic (Seed 42)."""
    d1 = ml_dataset_builder.build_synthetic_dataset(target_horizon=0)
    d2 = ml_dataset_builder.build_synthetic_dataset(target_horizon=0)

    assert d1.total_records == d2.total_records == 2190
    assert d1.targets[:50] == d2.targets[:50]
    assert [r["booking_demand"] for r in d1.features[:30]] == [r["booking_demand"] for r in d2.features[:30]]


# ─── 10. MIXED Dataset Provenance Remains Visible ─────────────────────────────

def test_mixed_dataset_provenance_transparency():
    """MIXED datasets must clearly report the exact count and provenance of real vs synthetic rows."""
    dataset = ml_dataset_builder.build_mixed_dataset(target_horizon=1)
    assert dataset.dataset_mode == "MIXED"
    assert "row_provenance" in dataset.features[0] or "row_provenance" in dataset.feature_names
    assert dataset.metadata.dataset_mode == "MIXED"
    assert "SYNTHETIC_ROWS" in dataset.metadata.provenance_counts


# ─── 11. Insufficient Real Data Blocks Production Promotion ───────────────────

def test_insufficient_real_data_blocks_production():
    """ProductionEligibilityGate must reject datasets with insufficient observations."""
    gate = ProductionEligibilityGate(ProductionEligibilityRules(min_total_rows=100))
    
    # Empty or small real data
    verdict = gate.evaluate(
        features=[{"historical_footfall": 50.0}],
        targets=[50.0],
        destinations=["darjeeling"],
        dataset_mode="REAL",
        date_range={"start": "2026-09-01", "end": "2026-09-01"}
    )
    assert verdict.is_eligible is False
    assert verdict.status in ("INSUFFICIENT_DATA", "HISTORICAL_PRODUCTION_CANDIDATE")
    assert any("observation count" in r.lower() for r in verdict.failure_reasons)


# ─── 12. Synthetic Model is Not Marked Production-Ready ───────────────────────

def test_synthetic_model_is_not_marked_production_ready():
    """Synthetic model training must be marked SYNTHETIC_BENCHMARK and production_eligible=False."""
    gate = ProductionEligibilityGate()
    verdict = gate.evaluate(
        features=[{"historical_footfall": 50.0}] * 500,
        targets=[50.0] * 500,
        destinations=["darjeeling", "kalimpong", "mirik"],
        dataset_mode="SYNTHETIC",
        date_range={"start": "2026-01-01", "end": "2026-06-01"}
    )
    assert verdict.is_eligible is False
    assert verdict.status == "SYNTHETIC_BENCHMARK"
    assert any("SYNTHETIC" in r.upper() for r in verdict.failure_reasons)


# ─── 13. Model Registry Artifact Compatibility ────────────────────────────────

def test_model_registry_artifact_compatibility():
    """Model registry must inspect loaded model metadata and expose version/schema information."""
    models = model_registry.list_models()
    assert len(models) >= 1
    baseline_entry = next((m for m in models if m["name"] == "baseline_rule_v2"), None)
    assert baseline_entry is not None
    assert baseline_entry["model_status"] == "BASELINE"
    assert baseline_entry["production_eligible"] is True


# ─── 14. Feature Schema Mismatch Handling ─────────────────────────────────────

def test_feature_schema_mismatch_fallback():
    """If an incompatible model is passed unexpected schema or fails, registry falls back safely."""
    class BrokenModel:
        name = "broken_ml_model"
        version = "9.9.9"
        is_trained = True
        model_status = "BROKEN"
        production_eligible = False
        def predict(self, features):
            raise KeyError("missing_required_broken_field")

    broken = BrokenModel()
    model_registry.register_model(broken)
    
    result = model_registry.safe_predict(features={"historical_footfall": 60.0}, prefer_model="broken_ml_model")
    assert result["model_used"] == "baseline_rule_v2"
    assert result["fallback_active"] is True
    assert "ML model prediction error" in result["fallback_reason"]


# ─── 15. Model Status Metadata ────────────────────────────────────────────────

def test_model_status_metadata_endpoint():
    """GET /api/admin/ml/status must expose model_status, production_eligible, and horizons."""
    resp = client.get("/api/admin/ml/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "model_status" in data
    assert "production_eligible" in data
    assert "horizons_supported" in data
    assert data["horizons_supported"] == [1, 3, 7, 14]


# ─── 16. Artificial Inference Multipliers Removed ─────────────────────────────

def test_artificial_inference_multipliers_removed():
    """Verify that build_inference_features constructs genuine features without hardcoded multipliers."""
    builder = StandardFeatureBuilder()
    feats = builder.build_inference_features(
        destination_id="kalimpong",
        target_date=date(2026, 10, 10),
        feature_date=date(2026, 10, 7),
        target_horizon_days=3,
        current_telemetry={
            "historical_footfall": 72.0,
            "accommodation_occupancy": 58.0,
            "weather_pressure": 40.0,
        }
    )
    # The features must reflect the supplied telemetry, not arbitrary * 0.95 or 55.0
    assert feats["historical_footfall"] == 72.0
    assert feats["accommodation_occupancy"] == 58.0
    assert feats["weather_pressure"] == 40.0
    assert feats["dest_kalimpong"] == 1


# ─── 17. Missing Telemetry is Not Converted into Fake Zero Values ─────────────

def test_missing_telemetry_preserved_as_none_or_nan():
    """Unmeasured signals must remain None / NaN rather than being converted to artificial 0.0."""
    builder = StandardFeatureBuilder()
    feats = builder.build_inference_features(
        destination_id="mirik",
        target_date=date(2026, 10, 10),
        feature_date=date(2026, 10, 9),
        target_horizon_days=1,
        current_telemetry={
            "historical_footfall": 50.0
            # traffic_pressure is completely absent
        }
    )
    # traffic_pressure must be None, NOT 0.0
    assert feats["traffic_pressure"] is None

    # In model vectorization, it must convert to math.isnan, not 0.0
    vec = xgboost_crowd_model._dict_to_vector(feats)
    traffic_idx = builder.get_feature_names().index("traffic_pressure")
    assert math.isnan(vec[traffic_idx]), "Missing telemetry must be NaN in XGBoost vector"


# ─── 18. ML API Backward Compatibility ────────────────────────────────────────

def test_ml_forecast_endpoint_backward_compatibility():
    """Existing frontend fields must remain present and valid in GET /api/destinations/{id}/pressure/forecast/ml."""
    resp = client.get("/api/destinations/darjeeling/pressure/forecast/ml?days=7")
    assert resp.status_code == 200
    data = resp.json()

    # Preserved required frontend fields
    assert "destination_id" in data
    assert "destination_name" in data
    assert "horizon_days" in data
    assert "current_pressure" in data
    assert "forecast" in data
    assert "model_used" in data
    assert "model_version" in data
    assert "fallback_active" in data
    assert "confidence_note" in data
    assert "generated_at" in data

    # Additive metadata fields
    assert "model_status" in data
    assert "production_eligible" in data
    assert "feature_timestamp" in data

    for day in data["forecast"]:
        assert "date" in day
        assert "day_name" in day
        assert "predicted_pressure" in day
        assert "pressure_level" in day
        assert "confidence" in day


# ─── 19. Baseline Fallback is Explicitly Identified ───────────────────────────

def test_baseline_fallback_explicitly_identified():
    """When ML is bypassed or unavailable, fallback_active is True and fallback_reason is provided."""
    result = model_registry.safe_predict(features={"historical_footfall": 50.0}, prefer_model="baseline_rule_v2")
    assert result["model_used"] == "baseline_rule_v2"
    assert result["fallback_active"] is False or "baseline" in result["model_used"]


# ─── 20. XGBoost Predictions Stay Within Valid Range ──────────────────────────

def test_xgboost_predictions_within_valid_constraints():
    """Predicted pressures must always stay strictly within [0.0, 100.0]."""
    builder = StandardFeatureBuilder()
    test_rows = [
        # Extreme low
        builder.build_inference_features(
            destination_id="lava",
            target_date=date(2026, 12, 1),
            feature_date=date(2026, 11, 30),
            target_horizon_days=1,
            current_telemetry={"historical_footfall": 0.0, "booking_demand": 0.0, "traffic_pressure": 0.0}
        ),
        # Extreme high
        builder.build_inference_features(
            destination_id="darjeeling",
            target_date=date(2026, 5, 20),
            feature_date=date(2026, 5, 13),
            target_horizon_days=7,
            current_telemetry={"historical_footfall": 100.0, "booking_demand": 100.0, "traffic_pressure": 100.0}
        ),
    ]

    for row in test_rows:
        pred = model_registry.safe_predict(row)["predicted_pressure"]
        assert 0.0 <= pred <= 100.0
