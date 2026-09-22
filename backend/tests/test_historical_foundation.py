"""
Unit & Integration Tests for Historical Tourism Data Foundation (Prompt 3 / Milestone 10).

Covers all 12 required test specifications:
1. historical observation creation
2. provenance preservation
3. missing signal remains NULL/UNAVAILABLE
4. duplicate/idempotent ingestion
5. time bucket alignment
6. REAL/HISTORICAL dataset contains no synthetic rows
7. SYNTHETIC dataset remains deterministic (Seed 42)
8. MIXED dataset reports correct provenance counts
9. future target timestamp is separated from feature timestamp (leakage prevention)
10. provider failure does not manufacture historical data
11. dataset metadata correctly reports source composition
12. existing Crowd Engine V2 behavior remains unchanged
"""

from datetime import datetime, date, timezone
import pytest
from unittest.mock import patch, MagicMock

from app.core.database import SessionLocal, init_db
from app.models.entities import HistoricalObservationModel
from app.models.historical import (
    SignalProvenanceRecord,
    HistoricalObservationCreate,
    HistoricalObservationRecord,
    DatasetMetadata,
)
from app.services.historical.ingestion_service import (
    HistoricalIngestionService,
    historical_ingestion_service,
)
from app.services.ml.dataset_builder import (
    MLDatasetBuilder,
    ml_dataset_builder,
    DatasetBuildResult,
)
from app.services.crowd_engine_v2 import crowd_engine_v2
from app.services.data_sources.base import DataSourceReading


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure all database tables are created before running tests."""
    init_db()


# 1. Historical observation creation
def test_historical_observation_creation():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        test_prov = {
            "booking_demand": SignalProvenanceRecord(
                source="POSTGRESQL_BOOKING_TELEMETRY",
                provider_mode="HISTORICAL",
                confidence=0.95,
                is_available=True,
                raw_value=15.0,
                raw_unit="confirmed_bookings"
            )
        }
        create_req = HistoricalObservationCreate(
            destination_id="kalimpong",
            observed_at=now,
            date_bucket="2026-09-15",
            booking_demand=42.5,
            current_crowd_pressure=48.0,
            signal_provenance=test_prov,
            dataset_mode="REAL"
        )
        record = historical_ingestion_service.ingest_observation(create_req, db=db)
        
        assert record.destination_id == "kalimpong"
        assert record.date_bucket == "2026-09-15"
        assert record.booking_demand == 42.5
        assert record.current_crowd_pressure == 48.0
        assert record.dataset_mode == "REAL"
        assert "booking_demand" in record.signal_provenance
        assert record.signal_provenance["booking_demand"].provider_mode == "HISTORICAL"
    finally:
        db.close()


# 2. Provenance preservation
def test_provenance_preservation():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        signal_prov = {
            "weather_pressure": SignalProvenanceRecord(
                source="LIVE_OPENWEATHERMAP_API",
                provider_mode="LIVE",
                confidence=0.90,
                is_available=True,
                raw_value=16.5,
                raw_unit="celsius"
            ),
            "traffic_pressure": SignalProvenanceRecord(
                source="LIVE_TOMTOM_FLOW",
                provider_mode="LIVE",
                confidence=0.88,
                is_available=True,
                raw_value=1.4,
                raw_unit="congestion_ratio"
            ),
            "current_crowd_pressure": SignalProvenanceRecord(
                source="COMPUTED_CROWD_ENGINE_V2",
                provider_mode="COMPUTED",
                confidence=0.92,
                is_available=True,
                raw_value=65.0,
                raw_unit="pressure_index"
            )
        }
        create_req = HistoricalObservationCreate(
            destination_id="darjeeling",
            observed_at=now,
            date_bucket="2026-09-16",
            weather_pressure=82.0,
            traffic_pressure=60.0,
            current_crowd_pressure=65.0,
            signal_provenance=signal_prov,
            dataset_mode="REAL"
        )
        record = historical_ingestion_service.ingest_observation(create_req, db=db)
        
        assert record.signal_provenance["weather_pressure"].source == "LIVE_OPENWEATHERMAP_API"
        assert record.signal_provenance["weather_pressure"].provider_mode == "LIVE"
        assert record.signal_provenance["traffic_pressure"].source == "LIVE_TOMTOM_FLOW"
        assert record.signal_provenance["traffic_pressure"].provider_mode == "LIVE"
        assert record.signal_provenance["current_crowd_pressure"].provider_mode == "COMPUTED"
    finally:
        db.close()


# 3. Missing signal remains NULL/UNAVAILABLE
def test_missing_signal_remains_null_unavailable():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        signal_prov = {
            "footfall": SignalProvenanceRecord(
                source="Mock Tourism Simulator (WBTDC Analog)",
                provider_mode="UNAVAILABLE",
                confidence=0.0,
                is_available=False,
                notes="Unmeasured in real environment; kept NULL"
            )
        }
        create_req = HistoricalObservationCreate(
            destination_id="mirik",
            observed_at=now,
            date_bucket="2026-09-17",
            footfall=None,  # Explicitly unmeasured
            accommodation_occupancy=None,
            current_crowd_pressure=35.0,
            signal_provenance=signal_prov,
            dataset_mode="REAL"
        )
        record = historical_ingestion_service.ingest_observation(create_req, db=db)
        
        # Verify unmeasured signals are strictly None in record and DB
        assert record.footfall is None
        assert record.accommodation_occupancy is None
        
        # Directly query SQLAlchemy model in DB to verify NULL column
        db_model = db.query(HistoricalObservationModel).filter_by(id=record.id).first()
        assert db_model.footfall is None
        assert db_model.accommodation_occupancy is None
        assert record.signal_provenance["footfall"].provider_mode == "UNAVAILABLE"
        assert record.signal_provenance["footfall"].confidence == 0.0
    finally:
        db.close()


# 4. Duplicate/idempotent ingestion
def test_duplicate_idempotent_ingestion():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        req1 = HistoricalObservationCreate(
            destination_id="lava",
            observed_at=now,
            date_bucket="2026-09-18",
            booking_demand=20.0,
            current_crowd_pressure=25.0,
            dataset_mode="REAL"
        )
        rec1 = historical_ingestion_service.ingest_observation(req1, db=db)
        
        # Second ingestion with updated reading for the same destination & date
        req2 = HistoricalObservationCreate(
            destination_id="lava",
            observed_at=now,
            date_bucket="2026-09-18",
            booking_demand=28.0,
            current_crowd_pressure=30.0,
            dataset_mode="REAL"
        )
        rec2 = historical_ingestion_service.ingest_observation(req2, db=db)
        
        # Must have the same deterministic ID
        assert rec1.id == rec2.id
        assert rec2.booking_demand == 28.0
        assert rec2.current_crowd_pressure == 30.0
        
        # Count rows in DB for this destination and date
        matching_count = db.query(HistoricalObservationModel).filter(
            HistoricalObservationModel.destination_id == "lava",
            HistoricalObservationModel.date_bucket == "2026-09-18",
            HistoricalObservationModel.dataset_mode == "REAL"
        ).count()
        assert matching_count == 1, "Idempotency violated: duplicate row created!"
    finally:
        db.close()


# 5. Time bucket alignment
def test_time_bucket_alignment():
    now = datetime(2026, 9, 20, 14, 30, 0, tzinfo=timezone.utc)
    create_req = HistoricalObservationCreate(
        destination_id="rishop",
        observed_at=now,
        date_bucket="2026-09-20",
        current_crowd_pressure=22.0,
        dataset_mode="REAL"
    )
    rec = historical_ingestion_service.ingest_observation(create_req)
    assert rec.date_bucket == "2026-09-20"
    assert rec.observed_at.strftime("%Y-%m-%d") == rec.date_bucket


# 6. REAL/HISTORICAL dataset contains no synthetic rows
def test_real_historical_dataset_contains_no_synthetic_rows():
    db = SessionLocal()
    try:
        # Build REAL dataset
        res = ml_dataset_builder.build_historical_dataset(db=db)
        
        assert res.dataset_mode == "REAL"
        assert res.synthetic_record_count == 0
        if res.total_records > 0:
            for row in res.features:
                assert row.get("row_provenance", "REAL") != "SYNTHETIC"
        assert "Zero synthetic data injected" in res.notes or "Zero genuine historical observations" in res.notes
    finally:
        db.close()


# 7. SYNTHETIC dataset remains deterministic
def test_synthetic_dataset_remains_deterministic():
    res1 = ml_dataset_builder.build_synthetic_dataset()
    res2 = ml_dataset_builder.build_synthetic_dataset()
    
    assert res1.dataset_mode == "SYNTHETIC"
    assert res1.total_records == 2190
    assert res1.synthetic_record_count == 2190
    assert res1.real_record_count == 0
    assert res1.targets == res2.targets
    assert len(res1.features) == len(res2.features)
    assert res1.features[0] == res2.features[0]


# 8. MIXED dataset reports correct provenance counts
def test_mixed_dataset_reports_correct_provenance_counts():
    db = SessionLocal()
    try:
        # Ensure at least 1 real observation exists
        historical_ingestion_service.capture_current_observation("darjeeling", date_bucket="2026-09-20", db=db)
        
        mixed = ml_dataset_builder.build_mixed_dataset(db=db)
        assert mixed.dataset_mode == "MIXED"
        assert mixed.real_record_count >= 1
        assert mixed.synthetic_record_count > 0
        assert mixed.total_records == mixed.real_record_count + mixed.synthetic_record_count
        assert mixed.metadata.provenance_counts["REAL_ROWS"] == mixed.real_record_count
        assert mixed.metadata.provenance_counts["SYNTHETIC_ROWS"] == mixed.synthetic_record_count

    finally:
        db.close()


# 9. Future target timestamp is separated from feature timestamp (Leakage Prevention)
def test_future_target_timestamp_separated_from_feature_timestamp():
    db = SessionLocal()
    try:
        # Insert two sequential observations for kalimpong
        now = datetime.now(timezone.utc)
        req_day1 = HistoricalObservationCreate(
            destination_id="kalimpong",
            observed_at=now,
            date_bucket="2026-10-01",
            current_crowd_pressure=40.0,
            booking_demand=35.0,
            dataset_mode="REAL"
        )
        req_day2 = HistoricalObservationCreate(
            destination_id="kalimpong",
            observed_at=now,
            date_bucket="2026-10-02",
            current_crowd_pressure=55.0,
            booking_demand=48.0,
            dataset_mode="REAL"
        )
        historical_ingestion_service.ingest_observation(req_day1, db=db)
        historical_ingestion_service.ingest_observation(req_day2, db=db)

        # Build historical dataset with H=1 day ahead forecasting
        res = ml_dataset_builder.build_historical_dataset(
            destinations=["kalimpong"],
            start_date="2026-10-01",
            end_date="2026-10-02",
            target_horizon=1,
            db=db
        )

        assert res.total_records >= 1
        paired_row = next(r for r in res.features if r["feature_timestamp"] == "2026-10-01")
        
        # Temporal separation verification:
        assert paired_row["feature_timestamp"] == "2026-10-01"
        assert paired_row["target_timestamp"] == "2026-10-02"
        assert paired_row["target_horizon_days"] == 1
        # Target pressure for day 1 must equal day 2's crowd pressure (55.0)
        assert paired_row["target_pressure"] == 55.0
        # Input features at day 1 must equal day 1's booking demand (35.0), NOT day 2 (48.0)
        assert paired_row["booking_demand"] == 35.0
        assert paired_row["feature_timestamp"] < paired_row["target_timestamp"]
    finally:
        db.close()


# 10. Provider failure does not manufacture historical data
def test_provider_failure_does_not_manufacture_data():
    db = SessionLocal()
    try:
        # Simulate weather provider throwing an exception
        with patch.object(
            crowd_engine_v2.providers["weather_pressure"],
            "get_reading",
            side_effect=Exception("External Weather API 503 Service Unavailable")
        ):
            rec = historical_ingestion_service.capture_current_observation(
                destination_id="lolegaon",
                date_bucket="2026-09-22",
                dataset_mode="REAL",
                db=db
            )
            # Must NOT fabricate a number; weather_pressure remains None
            assert rec.weather_pressure is None
            prov = rec.signal_provenance["weather_pressure"]
            assert prov.provider_mode in ("UNAVAILABLE", "DEMO")
            assert prov.confidence == 0.0
            assert "unmeasured" in prov.notes.lower() or "failed" in prov.notes.lower() or "suppressed" in prov.notes.lower()
    finally:
        db.close()


# 11. Dataset metadata correctly reports source composition
def test_dataset_metadata_reports_source_composition():
    synth_res = ml_dataset_builder.build_synthetic_dataset()
    meta: DatasetMetadata = synth_res.metadata

    assert meta.dataset_mode == "SYNTHETIC"
    assert meta.destination_count == 6
    assert meta.row_count == 2190
    assert meta.real_row_count == 0
    assert meta.synthetic_row_count == 2190
    assert meta.ml_eligible is False  # Synthetic data ineligible for production ML
    assert "SYNTHETIC" in meta.provenance_counts
    assert meta.leakage_prevention_verified is True


# 12. Existing Crowd Engine V2 behavior remains unchanged
def test_crowd_engine_v2_unaffected():
    from app.models.crowd import CrowdLevel
    # Canonical current crowd evaluation must remain completely intact
    crowd_resp = crowd_engine_v2.get_canonical_crowd_response("darjeeling")
    
    assert crowd_resp.destination_id == "darjeeling"
    assert 0.0 <= crowd_resp.crowd_score <= 100.0
    assert crowd_resp.crowd_level in [CrowdLevel.LOW, CrowdLevel.MEDIUM, CrowdLevel.HIGH, CrowdLevel.VERY_HIGH]
    assert crowd_resp.confidence_score > 0.0
    assert len(crowd_resp.factors) == 8
    assert crowd_resp.summary != ""
    assert len(crowd_resp.why_crowded) > 0


# 13. Historical API endpoints test
def test_historical_api_endpoints():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    # 1. GET /api/v1/historical/status
    res_status = client.get("/api/v1/historical/status")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["storage_status"] == "ACTIVE"
    assert "total_records" in status_data

    # 2. POST /api/v1/historical/ingest
    res_ingest = client.post("/api/v1/historical/ingest?destination_id=mirik&date_bucket=2026-09-25")
    assert res_ingest.status_code == 200
    ingest_data = res_ingest.json()
    assert ingest_data["status"] == "SUCCESS"
    assert ingest_data["observation"]["destination_id"] == "mirik"

    # 3. GET /api/v1/historical/observations
    res_obs = client.get("/api/v1/historical/observations?destination_id=mirik")
    assert res_obs.status_code == 200
    obs_list = res_obs.json()
    assert len(obs_list) >= 1
    assert obs_list[0]["destination_id"] == "mirik"

    # 4. GET /api/v1/historical/latest
    res_latest = client.get("/api/v1/historical/latest?destination_id=mirik")
    assert res_latest.status_code == 200
    latest_data = res_latest.json()
    assert latest_data["destination_id"] == "mirik"

    # 5. GET /api/v1/historical/provenance
    res_prov = client.get("/api/v1/historical/provenance?destination_id=mirik")
    assert res_prov.status_code == 200
    prov_data = res_prov.json()
    assert "signal_availability_percentages" in prov_data


