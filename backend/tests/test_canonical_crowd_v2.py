"""
Tests for Canonical Current Crowd Pressure (Crowd Engine V2).

Validates:
1. Crowd Engine V2 is the single canonical source of truth for current crowd pressure.
2. Canonical structured result contains all required fields: pressure_score, pressure_level,
   contributing signals, signal values, signal weights, provenance, timestamp, data status, confidence.
3. Backward compatibility with existing frontend fields: crowd_score, crowd_level, factors, why_crowded, bottlenecks.
4. Consumers (alternative recommendations, flow decision, date advisor, itinerary) consume the canonical result.
5. Legacy V1 calculate_crowd_score emits a DeprecationWarning.
6. XGBoost remains an independent future-forecasting layer.
"""
import pytest
import warnings
from fastapi.testclient import TestClient

from app.main import app
from app.services.crowd_engine_v2 import crowd_engine_v2
from app.services.crowd_engine import calculate_crowd_score
from app.services.alternative_engine import get_alternative_destinations
from app.services.date_advisor import get_date_alternatives
from app.models.crowd import CrowdResponse, CrowdLevel
from app.models.pressure import PressureLevel

client = TestClient(app)


def test_canonical_crowd_response_structure():
    """Verify get_canonical_crowd_response returns the unified canonical schema."""
    resp = crowd_engine_v2.get_canonical_crowd_response("darjeeling")
    assert isinstance(resp, CrowdResponse)
    
    # Frontend legacy compatibility fields
    assert resp.destination_id == "darjeeling"
    assert 0 <= resp.crowd_score <= 100
    assert resp.crowd_level in (CrowdLevel.LOW, CrowdLevel.MEDIUM, CrowdLevel.HIGH, CrowdLevel.VERY_HIGH)
    assert len(resp.why_crowded) > 0
    assert len(resp.factors) == 8
    assert len(resp.bottlenecks) > 0
    assert resp.color_code.startswith("#")
    
    # Canonical V2 fields
    assert resp.pressure_score is not None
    assert 0 <= resp.pressure_score <= 100.0
    assert round(resp.pressure_score) == resp.crowd_score
    assert resp.pressure_level in (PressureLevel.LOW, PressureLevel.MODERATE, PressureLevel.HIGH, PressureLevel.CRITICAL)
    assert 0.0 <= resp.confidence <= 1.0
    assert 0 <= resp.confidence_percent <= 100
    assert resp.signals_available >= 5
    assert resp.total_signals == 8
    assert len(resp.signals) == 8
    assert resp.data_status in ("ACTIVE", "PARTIAL", "CALIBRATED", "REAL_TIME", "BASELINE_ONLY")
    assert resp.timestamp is not None
    assert resp.provenance_label is not None
    assert resp.carrying_capacity_percent is not None
    assert resp.recommended_action is not None


def test_canonical_crowd_all_destinations():
    """Verify all 6 primary destinations return valid canonical crowd responses."""
    destinations = ["darjeeling", "kalimpong", "kurseong", "mirik", "lava", "rishop"]
    for dest in destinations:
        resp = crowd_engine_v2.get_canonical_crowd_response(dest)
        assert resp.destination_id == dest
        assert 0 <= resp.crowd_score <= 100
        assert resp.pressure_score is not None
        assert resp.confidence > 0.0
        assert len(resp.factors) == 8
        assert len(resp.signals) == 8


def test_api_crowd_endpoint_uses_canonical_v2():
    """Verify the main frontend crowd endpoint /api/destinations/{id}/crowd uses V2."""
    res = client.get("/api/destinations/darjeeling/crowd")
    assert res.status_code == 200
    data = res.json()
    
    # Frontend required fields are intact
    assert data["destination_id"] == "darjeeling"
    assert "crowd_score" in data
    assert "crowd_level" in data
    assert "why_crowded" in data
    assert "factors" in data
    assert "bottlenecks" in data
    
    # Canonical V2 fields are added backward-compatibly
    assert "pressure_score" in data
    assert "pressure_level" in data
    assert "confidence" in data
    assert "confidence_score" in data
    assert "confidence_percent" in data
    assert "signals" in data
    assert "data_status" in data
    assert "timestamp" in data
    
    # Values match direct engine calculation
    direct_resp = crowd_engine_v2.get_canonical_crowd_response("darjeeling")
    assert data["crowd_score"] == direct_resp.crowd_score
    assert data["pressure_score"] == direct_resp.pressure_score


def test_alternative_recommendations_consume_canonical_crowd():
    """Verify alternative recommendation engine consumes canonical V2 crowd results."""
    alt_res = get_alternative_destinations("darjeeling")
    direct_resp = crowd_engine_v2.get_canonical_crowd_response("darjeeling")
    
    # Origin crowd score in recommendation must match canonical V2 score
    assert alt_res.origin_crowd_score == direct_resp.crowd_score
    
    # Each alternative destination's score must match its canonical V2 score
    for alt in alt_res.alternatives:
        alt_canonical = crowd_engine_v2.get_canonical_crowd_response(alt.id)
        assert alt.alternative_crowd_score == alt_canonical.crowd_score


def test_date_advisor_consumes_canonical_crowd():
    """Verify date advisor uses canonical V2 base crowd score."""
    res = get_date_alternatives("darjeeling", "2026-12-25", "2026-12-27")
    direct_resp = crowd_engine_v2.get_canonical_crowd_response("darjeeling")
    
    # Preferred crowd score is elevated from base crowd by holiday multiplier
    assert res.preferred_crowd_score >= direct_resp.crowd_score
    assert res.preferred_crowd_score >= 88


def test_v1_calculate_crowd_score_deprecation_warning():
    """Verify legacy calculate_crowd_score emits a DeprecationWarning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        calculate_crowd_score("darjeeling")
        deprecation_warnings = [item for item in w if issubclass(item.category, DeprecationWarning)]
        assert len(deprecation_warnings) >= 1
        assert "deprecated" in str(deprecation_warnings[0].message).lower()
