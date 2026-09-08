import pytest
from app.services.crowd_engine import (
    calculate_crowd_score, classify_crowd_level, WEIGHTS
)
from app.models.crowd import CrowdLevel
from app.services.alternative_engine import get_alternative_destinations
from app.services.date_advisor import get_date_alternatives
from app.services.flow_decision_engine import compute_destination_decision

def test_weights_sum_to_one():
    """Verify deterministic crowd calculation weights sum exactly to 100%."""
    total_weight = sum(WEIGHTS.values())
    assert abs(total_weight - 1.0) < 1e-6

def test_crowd_classification_thresholds():
    """Verify 0-25 LOW, 26-50 MEDIUM, 51-75 HIGH, 76-100 VERY HIGH."""
    lvl, _ = classify_crowd_level(15)
    assert lvl == CrowdLevel.LOW

    lvl, _ = classify_crowd_level(25)
    assert lvl == CrowdLevel.LOW

    lvl, _ = classify_crowd_level(26)
    assert lvl == CrowdLevel.MEDIUM

    lvl, _ = classify_crowd_level(50)
    assert lvl == CrowdLevel.MEDIUM

    lvl, _ = classify_crowd_level(65)
    assert lvl == CrowdLevel.HIGH

    lvl, _ = classify_crowd_level(88)
    assert lvl == CrowdLevel.VERY_HIGH

def test_darjeeling_crowd_score():
    """Darjeeling during peak season must produce a VERY HIGH crowd score with explainability."""
    crowd = calculate_crowd_score("darjeeling")
    assert crowd.crowd_score >= 76
    assert crowd.crowd_level == CrowdLevel.VERY_HIGH
    assert len(crowd.why_crowded) > 0
    assert len(crowd.factors) == 6
    assert any("Tiger Hill" in r or "Mall" in r for r in crowd.why_crowded)

def test_kalimpong_crowd_score():
    """Kalimpong must register a moderate crowd score."""
    crowd = calculate_crowd_score("kalimpong")
    assert 26 <= crowd.crowd_score <= 50
    assert crowd.crowd_level == CrowdLevel.MEDIUM

def test_alternative_recommendations_for_darjeeling():
    """
    When searching alternatives for Darjeeling:
    - Kalimpong should be recommended with 87% similarity
    - Original crowd score should be 88
    - Alternative crowd score should be <= 50
    - Crowd reduction percent should be calculated properly (> 40%)
    - Matching attributes should be populated
    """
    alt_res = get_alternative_destinations("darjeeling")
    assert alt_res.origin_destination_id == "darjeeling"
    assert len(alt_res.alternatives) > 0

    top_alt = alt_res.alternatives[0]
    assert top_alt.id == "kalimpong"
    assert top_alt.similarity_score == 87
    assert top_alt.original_crowd_score >= 76
    assert top_alt.alternative_crowd_score <= 50
    assert top_alt.crowd_reduction_percent > 40
    assert len(top_alt.matching_attributes) > 0
    assert top_alt.cost_difference_percent < 0
    assert len(top_alt.reasons_to_recommend) >= 3

def test_date_advisor_recommendations():
    """
    When user requests peak dates for Darjeeling (e.g. 2026-12-25 to 2026-12-27):
    - Should return 3 calm alternative date windows
    - Each window should have a lower crowd score
    - Crowd reduction percent should be significant (> 50%)
    - Structured reasons and availability score must be present
    """
    res = get_date_alternatives("darjeeling", "2026-12-25", "2026-12-27")
    assert res.destination_id == "darjeeling"
    assert res.preferred_crowd_score >= 88
    assert res.preferred_crowd_classification == CrowdLevel.VERY_HIGH
    assert len(res.date_alternatives) == 3

    for alt in res.date_alternatives:
        assert alt.crowd_score < res.preferred_crowd_score
        assert alt.crowd_reduction_percent > 50
        assert alt.availability_score >= 80
        assert len(alt.reason) > 10

def test_date_advisor_deterministic_output():
    """Identical inputs must yield identical outputs."""
    res1 = get_date_alternatives("darjeeling", "2026-12-25", "2026-12-27")
    res2 = get_date_alternatives("darjeeling", "2026-12-25", "2026-12-27")
    assert res1.date_alternatives[0].crowd_score == res2.date_alternatives[0].crowd_score
    assert res1.date_alternatives[0].start_date == res2.date_alternatives[0].start_date

def test_date_advisor_invalid_inputs():
    """Invalid destination raises KeyError, invalid date range raises ValueError."""
    with pytest.raises(KeyError):
        get_date_alternatives("nonexistent_place", "2026-12-25", "2026-12-27")

    with pytest.raises(ValueError):
        get_date_alternatives("darjeeling", "2026-12-27", "2026-12-25") # end before start

    with pytest.raises(ValueError):
        get_date_alternatives("darjeeling", "invalid-date", "2026-12-27")

def test_flow_decision_engine():
    """
    High crowd destination (Darjeeling in Dec) should recommend CHANGE_DESTINATION
    due to high-similarity alternative Kalimpong.
    Low crowd destination (Lava) should recommend KEEP_DESTINATION.
    """
    darj_decision = compute_destination_decision("darjeeling", "2026-12-25", "2026-12-27")
    assert darj_decision.recommended_action == "CHANGE_DESTINATION"
    assert len(darj_decision.alternative_destinations) > 0
    assert len(darj_decision.alternative_dates) == 3

    lava_decision = compute_destination_decision("lava", "2026-12-25", "2026-12-27")
    assert lava_decision.recommended_action == "KEEP_DESTINATION"
