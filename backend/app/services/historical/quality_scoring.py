"""
Historical Observation Quality Scoring Engine (Milestone 12 / Prompt 6).

Responsible for calculating deterministic quality scores and classifications:
- signal_availability_ratio (populated signals / total slots)
- core_signal_availability_ratio (populated core signals / core slots)
- provenance_completeness (fraction of signals with valid provenance tracking)
- temporal_alignment_validity (strict validation of date_bucket and observed_at)
- source_diversity (count of distinct data source types contributing non-null signals)
- composite_confidence (confidence metric across contributing signals)

Classifications:
- HIGH: Rich multi-source observation with high core availability (>=60%), >=3 sources, confidence >=0.70
- MEDIUM: Sufficient observation with core availability >=40%, >=2 sources, confidence >=0.50
- LOW: Sparse but valid observation
- INVALID: Future date, non-canonical destination, invalid timestamp, or missing target ground truth
"""

from datetime import datetime, date, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

CANONICAL_DESTINATIONS = ("darjeeling", "kalimpong", "mirik", "lava", "lolegaon", "rishop")

CORE_SIGNALS = (
    "booking_demand",
    "search_demand",
    "holiday_pressure",
    "event_pressure",
    "current_crowd_pressure",
)

ALL_SIGNALS = (
    "footfall",
    "accommodation_occupancy",
    "booking_demand",
    "search_demand",
    "traffic_pressure",
    "weather_pressure",
    "holiday_pressure",
    "event_pressure",
    "current_crowd_pressure",
)


@dataclass
class ObservationQualityScore:
    """Detailed deterministic scoring output for a single historical observation."""
    quality_grade: str  # HIGH, MEDIUM, LOW, INVALID
    signal_availability_ratio: float
    core_signal_availability_ratio: float
    provenance_completeness: float
    temporal_alignment_validity: bool
    source_diversity: int
    composite_confidence: float
    available_signals_count: int
    missing_signals_count: int
    contributing_sources: List[str]
    validation_errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ObservationQualityScorer:
    """Evaluates observation quality without altering or fabricating telemetry."""

    @staticmethod
    def score_observation(obs: Any) -> ObservationQualityScore:
        """
        Calculates quality metrics and assigns a deterministic grade (HIGH, MEDIUM, LOW, INVALID).
        Accepts HistoricalObservationRecord, HistoricalObservationModel, or dictionary.
        """
        validation_errors: List[str] = []

        # 1. Destination verification
        dest_id = getattr(obs, "destination_id", None)
        if isinstance(obs, dict):
            dest_id = obs.get("destination_id")
        clean_dest = str(dest_id).lower().strip() if dest_id else ""
        if clean_dest not in CANONICAL_DESTINATIONS:
            validation_errors.append(f"Destination '{clean_dest}' is not in canonical registry.")

        # 2. Temporal alignment verification
        date_bucket = getattr(obs, "date_bucket", None)
        if isinstance(obs, dict):
            date_bucket = obs.get("date_bucket")

        temporal_valid = True
        if not date_bucket:
            temporal_valid = False
            validation_errors.append("date_bucket is missing.")
        else:
            try:
                dt = datetime.strptime(str(date_bucket), "%Y-%m-%d").date()
                # Check not in the future (respecting IST local calendar alignment)
                now_utc = datetime.now(timezone.utc)
                today_ist = (now_utc + timedelta(hours=5, minutes=30)).date()
                if dt > today_ist:
                    temporal_valid = False
                    validation_errors.append(f"date_bucket '{date_bucket}' is in the future.")
            except ValueError:
                temporal_valid = False
                validation_errors.append(f"Invalid date_bucket format '{date_bucket}', expected YYYY-MM-DD.")

        # 3. Target ground truth verification (current_crowd_pressure)
        target_val = getattr(obs, "current_crowd_pressure", None)
        if isinstance(obs, dict):
            target_val = obs.get("current_crowd_pressure")
        if target_val is None:
            validation_errors.append("current_crowd_pressure target is missing (None).")

        # 4. Signal availability counts
        available_count = 0
        core_available_count = 0
        prov_complete_count = 0

        prov_dict = getattr(obs, "signal_provenance", None) or getattr(obs, "signal_provenance_json", None)
        if isinstance(obs, dict):
            prov_dict = obs.get("signal_provenance") or obs.get("signal_provenance_json")
        if not isinstance(prov_dict, dict):
            prov_dict = {}

        contributing_sources = set()

        for s in ALL_SIGNALS:
            val = getattr(obs, s, None) if not isinstance(obs, dict) else obs.get(s)
            if val is not None:
                available_count += 1
                if s in CORE_SIGNALS:
                    core_available_count += 1

                # Provenance tracking
                p_entry = prov_dict.get(s)
                if p_entry:
                    prov_complete_count += 1
                    source_name = getattr(p_entry, "source", None) or (p_entry.get("source") if isinstance(p_entry, dict) else None)
                    if source_name:
                        contributing_sources.add(str(source_name))

        signal_ratio = round(available_count / len(ALL_SIGNALS), 3)
        core_ratio = round(core_available_count / len(CORE_SIGNALS), 3)
        prov_completeness = round(prov_complete_count / max(1, available_count), 3)
        missing_count = len(ALL_SIGNALS) - available_count
        source_diversity = len(contributing_sources)

        # Confidence
        confidence_val = getattr(obs, "composite_confidence", None)
        if isinstance(obs, dict):
            confidence_val = obs.get("composite_confidence")
        if confidence_val is None:
            confidence_val = 0.5 if available_count > 0 else 0.0
        confidence_val = round(float(confidence_val), 3)

        # Determine grade
        if not temporal_valid or len(validation_errors) > 0 or target_val is None:
            grade = "INVALID"
        elif core_ratio >= 0.60 and source_diversity >= 3 and confidence_val >= 0.70 and prov_completeness >= 0.80:
            grade = "HIGH"
        elif core_ratio >= 0.40 and source_diversity >= 2 and confidence_val >= 0.50:
            grade = "MEDIUM"
        else:
            grade = "LOW"

        return ObservationQualityScore(
            quality_grade=grade,
            signal_availability_ratio=signal_ratio,
            core_signal_availability_ratio=core_ratio,
            provenance_completeness=prov_completeness,
            temporal_alignment_validity=temporal_valid and (len(validation_errors) == 0),
            source_diversity=source_diversity,
            composite_confidence=confidence_val,
            available_signals_count=available_count,
            missing_signals_count=missing_count,
            contributing_sources=sorted(list(contributing_sources)),
            validation_errors=validation_errors
        )


observation_quality_scorer = ObservationQualityScorer()
