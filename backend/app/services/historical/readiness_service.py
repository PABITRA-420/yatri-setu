"""
Historical Readiness & Coverage Diagnostic Service (Prompt 7).

Provides dynamic, non-fabricated metrics on:
1. Historical observation accumulation progress toward ProductionEligibilityGate.
2. Six-destination coverage and representation analysis.
3. Signal availability, core missingness, and quality distribution.
4. Structural readiness projection (based strictly on observed daily row rate).
5. Scheduler and capture freshness monitoring.
"""

from datetime import datetime, timezone, timedelta, date
from typing import Dict, Any, List, Optional
import math
import logging
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.entities import HistoricalObservationModel
from app.services.historical.destination_registry import (
    CANONICAL_DESTINATIONS,
    normalize_destination_id,
)
from app.services.historical.quality_scoring import observation_quality_scorer
from app.services.ml.eligibility_gate import production_eligibility_gate
from app.services.ml.feature_builder import StandardFeatureBuilder

logger = logging.getLogger(__name__)

GATE_REQUIRED_ROWS = 180
GATE_REQUIRED_DAYS = 30
GATE_REQUIRED_DESTINATIONS = 3
GATE_REQUIRED_ROWS_PER_DEST = 20

CORE_SIGNALS = [
    "booking_demand",
    "search_demand",
    "holiday_pressure",
    "event_pressure",
    "current_crowd_pressure",
]

ALL_SIGNALS = [
    "footfall",
    "accommodation_occupancy",
    "booking_demand",
    "search_demand",
    "traffic_pressure",
    "weather_pressure",
    "holiday_pressure",
    "event_pressure",
    "current_crowd_pressure",
]


class HistoricalReadinessService:
    """
    Diagnostic service that audits real historical observation accumulation,
    measures progress against production gate criteria, and provides
    structural readiness projections without fabricating data.
    """

    def get_readiness_summary(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Calculates dynamic progress metrics against the ProductionEligibilityGate.
        Does NOT alter or weaken thresholds.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            now_utc = datetime.now(timezone.utc)
            rows = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == "REAL"
            ).all()

            total_real_observations = len(rows)

            # Prompt 9 Section 15: Clearly distinguish physical database audit records
            # from ML-eligible REAL observations. An invalid observation must NEVER increase ML eligibility.
            eligible_rows = []
            invalid_rows = []
            quality_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INVALID": 0}

            for r in rows:
                q = observation_quality_scorer.score_observation(r)
                grade = q.quality_grade if isinstance(q.quality_grade, str) else q.quality_grade.value
                quality_counts[grade] = quality_counts.get(grade, 0) + 1
                if grade != "INVALID":
                    eligible_rows.append(r)
                else:
                    invalid_rows.append(r)

            ml_eligible_real_observations = len(eligible_rows)
            invalid_audit_records = len(invalid_rows)

            # Dates and temporal span computed strictly from ML-eligible observations
            eligible_dates = sorted(list({r.date_bucket for r in eligible_rows if r.date_bucket}))
            distinct_dates_count = len(eligible_dates)

            earliest_date = eligible_dates[0] if eligible_dates else None
            latest_date = eligible_dates[-1] if eligible_dates else None

            if eligible_dates:
                d_min = datetime.strptime(earliest_date, "%Y-%m-%d").date()
                d_max = datetime.strptime(latest_date, "%Y-%m-%d").date()
                temporal_span_days = (d_max - d_min).days + 1
            else:
                temporal_span_days = 0

            # Destination breakdown strictly on ML-eligible observations
            dest_counts: Dict[str, int] = {d: 0 for d in CANONICAL_DESTINATIONS}
            dest_dates: Dict[str, set] = {d: set() for d in CANONICAL_DESTINATIONS}
            dest_latest: Dict[str, Optional[str]] = {d: None for d in CANONICAL_DESTINATIONS}

            total_core_checked = 0
            total_core_available = 0

            for r in eligible_rows:
                dest = r.destination_id
                if dest in dest_counts:
                    dest_counts[dest] += 1
                    dest_dates[dest].add(r.date_bucket)
                    if dest_latest[dest] is None or r.date_bucket > dest_latest[dest]:
                        dest_latest[dest] = r.date_bucket

                # Core signal check on eligible rows
                for cs in CORE_SIGNALS:
                    total_core_checked += 1
                    if getattr(r, cs, None) is not None:
                        total_core_available += 1

            destinations_present = sum(1 for cnt in dest_counts.values() if cnt > 0)
            destinations_underrepresented = [
                d for d, cnt in dest_counts.items() if cnt < GATE_REQUIRED_ROWS_PER_DEST
            ]
            min_rows_per_destination = min(dest_counts.values()) if dest_counts else 0

            # Core missingness on eligible observations
            if total_core_checked > 0:
                core_missingness_pct = round(
                    ((total_core_checked - total_core_available) / total_core_checked) * 100, 1
                )
                core_availability_pct = round((total_core_available / total_core_checked) * 100, 1)
            else:
                core_missingness_pct = 100.0
                core_availability_pct = 0.0

            # Progress percentages based strictly on ML-eligible observations
            row_progress_pct = round(min(100.0, (ml_eligible_real_observations / GATE_REQUIRED_ROWS) * 100), 2)
            temporal_progress_pct = round(
                min(100.0, (temporal_span_days / GATE_REQUIRED_DAYS) * 100), 2
            )

            # Evaluate through gate strictly on ML-eligible observations
            fb = StandardFeatureBuilder()
            features = []
            targets = []
            for r in eligible_rows:
                features.append(fb.build_feature_row(r))
                if r.current_crowd_pressure is not None:
                    targets.append(float(r.current_crowd_pressure))

            gate_verdict = production_eligibility_gate.evaluate(
                features=features,
                targets=targets,
                destinations=[d for d, c in dest_counts.items() if c > 0],
                dataset_mode="REAL",
                date_range={"start": earliest_date or "", "end": latest_date or ""},
            )

            # Remaining requirements calculations (Prompt 9 Section 22)
            remaining_rows_required = max(0, GATE_REQUIRED_ROWS - ml_eligible_real_observations)
            remaining_days_required = max(0, GATE_REQUIRED_DAYS - temporal_span_days)
            remaining_destination_depth = max(0, GATE_REQUIRED_ROWS_PER_DEST - min_rows_per_destination)

            # Structural projection strictly on eligible observations
            projection = self._calculate_structural_projection(
                real_rows=ml_eligible_real_observations,
                temporal_span_days=temporal_span_days,
                distinct_dates_count=distinct_dates_count,
                latest_date_str=latest_date,
            )

            target_variance = round(float(gate_verdict.target_variance), 3) if hasattr(gate_verdict, "target_variance") else 0.0
            target_availability_pct = round(float(gate_verdict.target_availability_percent), 1) if hasattr(gate_verdict, "target_availability_percent") else 100.0

            return {
                # Distinct row accounting
                "total_real_observations": total_real_observations,
                "total_real_rows": total_real_observations,
                "ml_eligible_real_observations": ml_eligible_real_observations,
                "ml_eligible_real_rows": ml_eligible_real_observations,
                "invalid_audit_records": invalid_audit_records,
                "invalid_rows": invalid_audit_records,
                "real_rows": ml_eligible_real_observations,  # Backward compatibility alias
                "required_rows": GATE_REQUIRED_ROWS,
                "row_progress_percent": row_progress_pct,
                # Temporal metrics
                "distinct_dates": distinct_dates_count,
                "unique_dates": distinct_dates_count,
                "unique_observation_dates": distinct_dates_count,
                "required_temporal_span_days": GATE_REQUIRED_DAYS,
                "temporal_span_days": temporal_span_days,
                "temporal_span": temporal_span_days,
                "temporal_progress_percent": temporal_progress_pct,
                "earliest_date": earliest_date,
                "latest_date": latest_date,
                "oldest_observation_date": earliest_date,
                "latest_observation_date": latest_date,
                # Destination representation
                "destinations_present": destinations_present,
                "destination_count": destinations_present,
                "required_destinations": GATE_REQUIRED_DESTINATIONS,
                "total_canonical_destinations": len(CANONICAL_DESTINATIONS),
                "rows_per_destination": dest_counts,
                "rows_by_destination": dest_counts,
                "min_rows_per_destination": min_rows_per_destination,
                "minimum_destination_depth": min_rows_per_destination,
                "destinations_underrepresented": destinations_underrepresented,
                "destination_freshness": dest_latest,
                # Signal and target quality
                "core_signal_missingness_percent": core_missingness_pct,
                "core_missingness": core_missingness_pct,
                "core_signal_availability_percent": core_availability_pct,
                "target_availability": target_availability_pct,
                "target_availability_percent": target_availability_pct,
                "target_variance": target_variance,
                "quality_breakdown": quality_counts,
                # Gate verdict and remaining requirements
                "eligible": gate_verdict.eligible,
                "gate_status": "ELIGIBLE" if gate_verdict.eligible else "INSUFFICIENT_DATA",
                "failed_requirements": gate_verdict.failed_requirements,
                "requirements_breakdown": getattr(gate_verdict, "requirements_breakdown", {}),
                "remaining_rows_required": remaining_rows_required,
                "rows_remaining": remaining_rows_required,
                "remaining_days_required": remaining_days_required,
                "days_remaining": remaining_days_required,
                "remaining_destination_depth_required": remaining_destination_depth,
                "destination_rows_remaining": remaining_destination_depth,
                # Diagnostic projection
                "projection": projection,
                "audited_at": now_utc.isoformat(),
            }
        finally:
            if close_db and db:
                db.close()

    def _calculate_structural_projection(
        self,
        real_rows: int,
        temporal_span_days: int,
        distinct_dates_count: int,
        latest_date_str: Optional[str],
    ) -> Dict[str, Any]:
        """
        Calculates when structural data requirements could be satisfied.
        Strictly based on observed unique-row rate.
        Never predicts XGBoost accuracy or business outcomes.
        """
        if distinct_dates_count < 2 or real_rows < 6 or not latest_date_str:
            return {
                "available": False,
                "reason": "insufficient_accumulation_history",
                "notes": (
                    f"Requires at least 2 distinct dates and 6 genuine rows to project. "
                    f"Current: {distinct_dates_count} dates, {real_rows} rows."
                ),
            }

        effective_days = max(1, temporal_span_days)
        daily_rate = real_rows / effective_days

        if daily_rate <= 0:
            return {
                "available": False,
                "reason": "non_positive_accumulation_rate",
            }

        rows_needed = max(0, GATE_REQUIRED_ROWS - real_rows)
        days_for_rows = math.ceil(rows_needed / daily_rate)
        days_for_span = max(0, GATE_REQUIRED_DAYS - temporal_span_days)

        days_to_ready = max(days_for_rows, days_for_span)

        try:
            latest_dt = datetime.strptime(latest_date_str, "%Y-%m-%d").date()
            est_ready_date = (latest_dt + timedelta(days=days_to_ready)).strftime("%Y-%m-%d")
        except Exception:
            est_ready_date = None

        return {
            "available": True,
            "projection_type": "STRUCTURAL_ACCUMULATION_PROJECTION",
            "label": "STRUCTURAL ACCUMULATION PROJECTION",
            "method": "observed_unique_real_row_rate",
            "estimated_gate_ready_date": est_ready_date,
            "estimated_days_to_gate_ready": days_to_ready,
            "daily_accumulation_rate_observed": round(daily_rate, 2),
            "rows_needed": rows_needed,
            "assumptions": [
                "current daily accumulation rate continues",
                "no change to eligibility thresholds",
                "all six canonical destinations continue to accumulate observations",
            ],
            "disclaimer": (
                "This is a data accumulation projection, not a prediction of model accuracy. "
                "Structural data projection only. Does not guarantee ML model accuracy "
                "or forecast skill upon reaching eligibility."
            ),
        }

    def get_destination_coverage(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Produces detailed six-destination coverage diagnostics (Prompt 7 Section 16).
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            now_utc = datetime.now(timezone.utc)
            today_date = now_utc.date()

            rows = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == "REAL"
            ).all()

            # Group by canonical destination
            by_dest: Dict[str, List[HistoricalObservationModel]] = {d: [] for d in CANONICAL_DESTINATIONS}
            for r in rows:
                if r.destination_id in by_dest:
                    by_dest[r.destination_id].append(r)

            destinations_report = []
            represented_count = 0
            underrepresented = []

            for dest in CANONICAL_DESTINATIONS:
                d_rows = by_dest[dest]
                row_count = len(d_rows)
                if row_count > 0:
                    represented_count += 1
                if row_count < GATE_REQUIRED_ROWS_PER_DEST:
                    underrepresented.append(dest)

                d_dates = sorted([r.date_bucket for r in d_rows if r.date_bucket])
                first_obs = d_dates[0] if d_dates else None
                latest_obs = d_dates[-1] if d_dates else None

                days_since_latest = None
                if latest_obs:
                    try:
                        lat_dt = datetime.strptime(latest_obs, "%Y-%m-%d").date()
                        days_since_latest = (today_date - lat_dt).days
                    except Exception:
                        pass

                # Latest quality & signals
                latest_quality = "UNAVAILABLE"
                avail_sig_count = 0
                missing_sig_count = len(ALL_SIGNALS)

                if d_rows:
                    # sort by date_bucket descending
                    sorted_rows = sorted(d_rows, key=lambda x: x.date_bucket, reverse=True)
                    latest_rec = sorted_rows[0]
                    q = observation_quality_scorer.score_observation(latest_rec)
                    latest_quality = q.quality_grade if isinstance(q.quality_grade, str) else q.quality_grade.value
                    avail_sig_count = q.available_signals_count
                    missing_sig_count = q.missing_signals_count

                destinations_report.append({
                    "destination": dest,
                    "real_rows": row_count,
                    "distinct_dates": len(set(d_dates)),
                    "first_observation": first_obs,
                    "latest_observation": latest_obs,
                    "days_since_latest": days_since_latest,
                    "latest_quality": latest_quality,
                    "available_signal_count": avail_sig_count,
                    "missing_signal_count": missing_sig_count,
                    "is_underrepresented": row_count < GATE_REQUIRED_ROWS_PER_DEST,
                })

            return {
                "total_canonical_destinations": len(CANONICAL_DESTINATIONS),
                "destinations_represented": represented_count,
                "destinations_underrepresented": underrepresented,
                "destinations": destinations_report,
                "generated_at": now_utc.isoformat(),
            }
        finally:
            if close_db and db:
                db.close()


historical_readiness_service = HistoricalReadinessService()
