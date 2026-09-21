"""
Daily Accumulation Health, Gap Monitoring & Capture Reliability Service (Milestone 13 / Prompt 12).

Responsible for:
1. Auditing genuine daily historical accumulation health across all 6 canonical destinations.
2. Managing the durable DailyCaptureLedgerModel for each (destination, observation_date) pair.
3. Classifying daily operational statuses:
   - CAPTURED_VALID: Legitimate observation passing quality rules and ML-eligible.
   - CAPTURED_INVALID: Observation present but quarantined due to quality failures.
   - MISSING: Expected destination/date pair absent from database.
   - INCOMPLETE: Observation present but missing ground-truth crowd pressure target.
   - DUPLICATE: Multiple records conflicting with uniqueness rules.
   - EXPECTED: Canonical destination/date expected in audit window.
4. Auditing operational status and freshness of all genuine telemetry data sources:
   - FRESH, STALE, UNAVAILABLE, UNKNOWN
   - Strictly prohibiting fabricated fallbacks when sources fail.
5. Calculating per-destination accumulation streaks and remaining depth to 20 rows.
6. Calculating actual recent accumulation velocity (1d, 7d, 14d, 30d) without inventing rates.
7. Providing hardened structural projections explicitly marked as PROJECTED (never GUARANTEED).
8. Integrating with ProductionEligibilityGate without weakening or duplicating thresholds.
"""

import math
import logging
from datetime import datetime, date, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.core.database import SessionLocal, engine
from app.models.entities import (
    HistoricalObservationModel,
    DailyCaptureLedgerModel,
    DestinationModel,
)
from app.services.historical.destination_registry import (
    CANONICAL_DESTINATIONS,
    normalize_destination_id,
)
from app.services.historical.quality_scoring import (
    observation_quality_scorer,
    ObservationQualityScore,
    CORE_SIGNALS,
    ALL_SIGNALS,
)
from app.services.ml.eligibility_gate import (
    production_eligibility_gate,
    ProductionEligibilityVerdict,
    ProductionEligibilityRules,
)
from app.services.historical.readiness_service import (
    GATE_REQUIRED_ROWS as GATE_MIN_ROWS,
    GATE_REQUIRED_DAYS as GATE_MIN_TEMPORAL_SPAN_DAYS,
    GATE_REQUIRED_DESTINATIONS as GATE_MIN_DESTINATIONS,
    GATE_REQUIRED_ROWS_PER_DEST as GATE_MIN_ROWS_PER_DESTINATION,
)

logger = logging.getLogger(__name__)

# Daily Completeness Statuses
STATUS_FULL_SUCCESS = "FULL_SUCCESS"
STATUS_PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
STATUS_FAILED = "FAILED"

# Observation Operational Statuses
STATUS_CAPTURED_VALID = "CAPTURED_VALID"
STATUS_CAPTURED_INVALID = "CAPTURED_INVALID"
STATUS_MISSING = "MISSING"
STATUS_INCOMPLETE = "INCOMPLETE"
STATUS_DUPLICATE = "DUPLICATE"
STATUS_EXPECTED = "EXPECTED"

# Source Freshness Statuses
FRESHNESS_FRESH = "FRESH"
FRESHNESS_STALE = "STALE"
FRESHNESS_UNAVAILABLE = "UNAVAILABLE"
FRESHNESS_UNKNOWN = "UNKNOWN"

# Freshness Threshold: 24 hours (86400 seconds)
SOURCE_FRESHNESS_THRESHOLD_HOURS = 24

# Legitimate telemetry sources monitored
KNOWN_DATA_SOURCES = [
    {
        "source_key": "weather",
        "provider_name": "OPEN_METEO_LIVE",
        "description": "Live mountain meteorological API (temperature, precipitation, comfort index)",
    },
    {
        "source_key": "bookings",
        "provider_name": "POSTGRESQL_BOOKINGS",
        "description": "Production database bookings repository (homestay reservation volume)",
    },
    {
        "source_key": "accommodation",
        "provider_name": "HOMESTAY_INVENTORY",
        "description": "Panchayat-registered homestay room availability & occupancy",
    },
    {
        "source_key": "search_demand",
        "provider_name": "DEMAND_EVENTS_NETWORK",
        "description": "Yatri Setu traveler discovery & itinerary search telemetry",
    },
    {
        "source_key": "events",
        "provider_name": "EVENTS_ENGINE",
        "description": "Local cultural & Himalayan festival registry",
    },
    {
        "source_key": "holidays",
        "provider_name": "HOLIDAY_ENGINE",
        "description": "Gazetted regional calendar surge multiplier",
    },
    {
        "source_key": "traffic",
        "provider_name": "CORRIDOR_TRAFFIC",
        "description": "Himalayan transit corridor checkpoint delay observations",
    },
    {
        "source_key": "crowd_engine_v2",
        "provider_name": "CROWD_ENGINE_V2_COMPUTED",
        "description": "Multi-signal deterministic crowd pressure target",
    },
]


class AccumulationHealthService:
    """
    Core service delivering deep observability, gap auditing, source health,
    streak tracking, velocity calculation, and ledger management for genuine historical accumulation.
    """

    def __init__(self):
        self._ensure_tables_exist()

    def _ensure_tables_exist(self):
        """Ensures both historical observations and daily capture ledger tables exist."""
        try:
            DailyCaptureLedgerModel.__table__.create(bind=engine, checkfirst=True)
            HistoricalObservationModel.__table__.create(bind=engine, checkfirst=True)
        except Exception as e:
            logger.debug(f"AccumulationHealthService table creation check: {e}")

    def _generate_ledger_id(self, destination_id: str, date_bucket: str, dataset_mode: str = "REAL") -> str:
        """Deterministic ledger entry identifier."""
        dest_clean = normalize_destination_id(destination_id)
        mode_clean = dataset_mode.upper().strip()
        return f"{dest_clean}_{date_bucket}_{mode_clean.lower()}"

    def record_daily_ledger_entry(
        self,
        destination_id: str,
        date_bucket: str,
        dataset_mode: str = "REAL",
        attempted: bool = True,
        attempts_count: int = 1,
        retry_count: int = 0,
        sources_attempted: Optional[List[str]] = None,
        sources_succeeded: Optional[List[str]] = None,
        sources_failed: Optional[List[Dict[str, Any]]] = None,
        validation_passed: bool = False,
        validation_errors: Optional[List[str]] = None,
        ml_eligible: bool = False,
        is_quarantined: bool = False,
        quarantine_reason: Optional[str] = None,
        is_duplicate: bool = False,
        final_status: str = STATUS_EXPECTED,
        provenance_summary: Optional[Dict[str, Any]] = None,
        observation_record_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> DailyCaptureLedgerModel:
        """
        Idempotently inserts or updates an operational audit record in the daily_capture_ledger table.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            dest_clean = normalize_destination_id(destination_id)
            mode_clean = dataset_mode.upper().strip()
            ledger_id = self._generate_ledger_id(dest_clean, date_bucket, mode_clean)
            now = datetime.now(timezone.utc)

            entry = db.query(DailyCaptureLedgerModel).filter(
                DailyCaptureLedgerModel.id == ledger_id
            ).first()

            if entry is None:
                entry = DailyCaptureLedgerModel(
                    id=ledger_id,
                    destination_id=dest_clean,
                    date_bucket=date_bucket,
                    dataset_mode=mode_clean,
                    attempted=attempted,
                    attempted_at=now,
                    completed_at=now,
                    attempts_count=attempts_count,
                    retry_count=retry_count,
                    sources_attempted_json=sources_attempted or [],
                    sources_succeeded_json=sources_succeeded or [],
                    sources_failed_json=sources_failed or [],
                    validation_passed=validation_passed,
                    validation_errors_json=validation_errors or [],
                    ml_eligible=ml_eligible,
                    is_quarantined=is_quarantined,
                    quarantine_reason=quarantine_reason,
                    is_duplicate=is_duplicate,
                    final_status=final_status,
                    provenance_summary_json=provenance_summary or {},
                    observation_record_id=observation_record_id,
                    created_at=now,
                    updated_at=now,
                )
                db.add(entry)
            else:
                entry.attempted = attempted
                entry.completed_at = now
                entry.attempts_count = max(entry.attempts_count or 1, attempts_count)
                entry.retry_count = max(entry.retry_count or 0, retry_count)
                entry.sources_attempted_json = sources_attempted or entry.sources_attempted_json
                entry.sources_succeeded_json = sources_succeeded or entry.sources_succeeded_json
                entry.sources_failed_json = sources_failed or entry.sources_failed_json
                entry.validation_passed = validation_passed
                entry.validation_errors_json = validation_errors or entry.validation_errors_json
                entry.ml_eligible = ml_eligible
                entry.is_quarantined = is_quarantined
                entry.quarantine_reason = quarantine_reason or entry.quarantine_reason
                entry.is_duplicate = is_duplicate
                entry.final_status = final_status
                entry.provenance_summary_json = provenance_summary or entry.provenance_summary_json
                entry.observation_record_id = observation_record_id or entry.observation_record_id
                entry.updated_at = now

            db.commit()
            db.refresh(entry)
            return entry
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to record daily ledger entry for {destination_id}/{date_bucket}: {e}")
            raise
        finally:
            if close_db and db:
                db.close()

    def get_source_health(self, db: Optional[Session] = None) -> List[Dict[str, Any]]:
        """
        Inspects operational health, latest success, latest attempt, age, and freshness
        of all legitimate telemetry sources from real records and ledger entries.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            now_utc = datetime.now(timezone.utc)
            source_results = []

            # Query the latest real observations to extract actual signal timestamps & provenance
            recent_obs = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == "REAL"
            ).order_by(HistoricalObservationModel.observed_at.desc()).limit(30).all()

            for src in KNOWN_DATA_SOURCES:
                s_key = src["source_key"]
                p_name = src["provider_name"]

                latest_success_dt: Optional[datetime] = None
                latest_attempt_dt: Optional[datetime] = None
                latest_value: Optional[float] = None
                status = "AVAILABLE"
                notes = ""

                # Audit observations for signal presence
                for obs in recent_obs:
                    val = None
                    if s_key == "weather":
                        val = obs.weather_pressure
                    elif s_key == "bookings":
                        val = obs.booking_demand
                    elif s_key == "accommodation":
                        val = obs.accommodation_occupancy
                    elif s_key == "search_demand":
                        val = obs.search_demand
                    elif s_key == "events":
                        val = obs.event_pressure
                    elif s_key == "holidays":
                        val = obs.holiday_pressure
                    elif s_key == "traffic":
                        val = obs.traffic_pressure
                    elif s_key == "crowd_engine_v2":
                        val = obs.current_crowd_pressure

                    obs_dt = obs.observed_at
                    if obs_dt and obs_dt.tzinfo is None:
                        obs_dt = obs_dt.replace(tzinfo=timezone.utc)

                    if latest_attempt_dt is None or (obs_dt and obs_dt > latest_attempt_dt):
                        latest_attempt_dt = obs_dt

                    if val is not None:
                        if latest_success_dt is None or (obs_dt and obs_dt > latest_success_dt):
                            latest_success_dt = obs_dt
                            latest_value = val
                            break

                # Calculate age and freshness
                age_seconds: Optional[float] = None
                freshness_status = FRESHNESS_UNKNOWN

                if latest_success_dt:
                    age_seconds = max(0.0, (now_utc - latest_success_dt).total_seconds())
                    hours_old = age_seconds / 3600.0
                    if hours_old <= SOURCE_FRESHNESS_THRESHOLD_HOURS:
                        freshness_status = FRESHNESS_FRESH
                    else:
                        freshness_status = FRESHNESS_STALE
                elif latest_attempt_dt:
                    freshness_status = FRESHNESS_UNAVAILABLE
                    status = "FAILED"
                    notes = "Source attempted but yielded no legitimate measurement."
                else:
                    freshness_status = FRESHNESS_UNKNOWN
                    notes = "No telemetry attempts recorded yet."

                source_results.append({
                    "source_name": p_name,
                    "signal_key": s_key,
                    "description": src["description"],
                    "status": "OPERATIONAL" if freshness_status == FRESHNESS_FRESH else ("STALE" if freshness_status == FRESHNESS_STALE else "UNAVAILABLE"),
                    "freshness_status": freshness_status,
                    "last_success_at": latest_success_dt.isoformat() if latest_success_dt else None,
                    "last_attempt_at": latest_attempt_dt.isoformat() if latest_attempt_dt else None,
                    "age_seconds": round(age_seconds, 1) if age_seconds is not None else None,
                    "latest_value": latest_value,
                    "notes": notes,
                })

            return source_results
        finally:
            if close_db and db:
                db.close()

    def get_destination_streaks(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Calculates accumulation streaks, last valid capture date, last invalid/missing date,
        eligible row count, and remaining depth to 20 for all 6 canonical destinations.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            now_utc = datetime.now(timezone.utc)

            # Retrieve all REAL records
            rows = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == "REAL"
            ).all()

            by_dest: Dict[str, List[HistoricalObservationModel]] = {d: [] for d in CANONICAL_DESTINATIONS}
            for r in rows:
                if r.destination_id in by_dest:
                    by_dest[r.destination_id].append(r)

            destination_streak_results = []
            for dest in CANONICAL_DESTINATIONS:
                d_rows = by_dest[dest]

                valid_rows = []
                invalid_rows = []

                for r in d_rows:
                    q = observation_quality_scorer.score_observation(r)
                    grade = q.quality_grade if isinstance(q.quality_grade, str) else q.quality_grade.value
                    if grade != "INVALID":
                        valid_rows.append(r)
                    else:
                        invalid_rows.append(r)

                valid_dates = sorted(list({r.date_bucket for r in valid_rows if r.date_bucket}))
                invalid_dates = sorted(list({r.date_bucket for r in invalid_rows if r.date_bucket}))

                last_valid = valid_dates[-1] if valid_dates else None
                last_invalid = invalid_dates[-1] if invalid_dates else None

                # Calculate consecutive streak leading up to last valid capture
                streak = 0
                if valid_dates:
                    d_objs = [datetime.strptime(dt, "%Y-%m-%d").date() for dt in valid_dates]
                    streak = 1
                    for i in range(len(d_objs) - 1, 0, -1):
                        if (d_objs[i] - d_objs[i - 1]).days == 1:
                            streak += 1
                        else:
                            break

                # Calculate last missing date within available range if any gap
                last_missing = None
                if valid_dates:
                    d_start = datetime.strptime(valid_dates[0], "%Y-%m-%d").date()
                    d_end = datetime.strptime(valid_dates[-1], "%Y-%m-%d").date()
                    v_set = set(valid_dates)
                    curr = d_start
                    while curr <= d_end:
                        c_str = curr.strftime("%Y-%m-%d")
                        if c_str not in v_set:
                            last_missing = c_str
                        curr += timedelta(days=1)

                eligible_count = len(valid_rows)
                remaining_to_20 = max(0, GATE_MIN_ROWS_PER_DESTINATION - eligible_count)

                destination_streak_results.append({
                    "destination": dest,
                    "destination_id": dest,
                    "eligible_rows": eligible_count,
                    "eligible_row_count": eligible_count,
                    "remaining_to_20": remaining_to_20,
                    "is_depth_satisfied": eligible_count >= GATE_MIN_ROWS_PER_DESTINATION,
                    "current_valid_streak": streak,
                    "last_valid_capture_date": last_valid,
                    "last_invalid_date": last_invalid,
                    "last_missing_date": last_missing,
                    "status": "HEALTHY" if remaining_to_20 == 0 else ("ACCUMULATING" if eligible_count > 0 else "INACTIVE"),
                })

            return {
                "destinations": destination_streak_results,
                "audited_at": now_utc.isoformat(),
            }
        finally:
            if close_db and db:
                db.close()

    def get_accumulation_velocity(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Calculates actual recent accumulation velocity strictly from eligible REAL rows.
        Does NOT assume 6 rows/day. Returns INSUFFICIENT_HISTORY when history is lacking.
        INVALID and synthetic rows are strictly excluded.
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

            # Filter strictly eligible rows
            eligible_rows = []
            for r in rows:
                q = observation_quality_scorer.score_observation(r)
                grade = q.quality_grade if isinstance(q.quality_grade, str) else q.quality_grade.value
                if grade != "INVALID":
                    eligible_rows.append(r)

            if not eligible_rows:
                return {
                    "eligible_rows_last_1_day": 0,
                    "eligible_rows_last_7_days": 0,
                    "eligible_rows_last_14_days": 0,
                    "eligible_rows_last_30_days": 0,
                    "average_daily_eligible_rows_7d": "INSUFFICIENT_HISTORY",
                    "average_daily_eligible_rows_14d": "INSUFFICIENT_HISTORY",
                    "average_daily_eligible_rows_30d": "INSUFFICIENT_HISTORY",
                    "status": "INSUFFICIENT_HISTORY",
                    "notes": "No eligible real historical observations found.",
                }

            all_dates = sorted(list({r.date_bucket for r in eligible_rows if r.date_bucket}))
            latest_date_str = all_dates[-1]
            latest_dt = datetime.strptime(latest_date_str, "%Y-%m-%d").date()

            # Group eligible rows by date_bucket
            date_counts: Dict[str, int] = {}
            for r in eligible_rows:
                date_counts[r.date_bucket] = date_counts.get(r.date_bucket, 0) + 1

            def count_rows_in_days(days_back: int) -> Tuple[int, int]:
                """Returns (total_rows, distinct_calendar_days_with_data) in window [latest_dt - days_back + 1, latest_dt]"""
                start_win = latest_dt - timedelta(days=days_back - 1)
                total = 0
                days_with_data = 0
                curr = start_win
                while curr <= latest_dt:
                    c_str = curr.strftime("%Y-%m-%d")
                    if c_str in date_counts:
                        total += date_counts[c_str]
                        days_with_data += 1
                    curr += timedelta(days=1)
                return total, days_with_data

            rows_1d, days_1d = count_rows_in_days(1)
            rows_7d, days_7d = count_rows_in_days(7)
            rows_14d, days_14d = count_rows_in_days(14)
            rows_30d, days_30d = count_rows_in_days(30)

            # Check temporal history sufficiency for rates
            avg_7d = round(rows_7d / 7.0, 2) if days_7d >= 2 else "INSUFFICIENT_HISTORY"
            avg_14d = round(rows_14d / 14.0, 2) if days_14d >= 4 else "INSUFFICIENT_HISTORY"
            avg_30d = round(rows_30d / 30.0, 2) if days_30d >= 7 else "INSUFFICIENT_HISTORY"

            # Overall observed accumulation rate (total eligible rows / total temporal span)
            earliest_dt = datetime.strptime(all_dates[0], "%Y-%m-%d").date()
            total_temporal_span = max(1, (latest_dt - earliest_dt).days + 1)
            overall_rate = round(len(eligible_rows) / total_temporal_span, 2)

            return {
                "eligible_rows_last_1_day": rows_1d,
                "eligible_rows_last_7_days": rows_7d,
                "eligible_rows_last_14_days": rows_14d,
                "eligible_rows_last_30_days": rows_30d,
                "average_daily_eligible_rows_7d": avg_7d,
                "average_daily_eligible_rows_14d": avg_14d,
                "average_daily_eligible_rows_30d": avg_30d,
                "overall_observed_rate_daily": overall_rate,
                "total_eligible_rows": len(eligible_rows),
                "total_distinct_dates": len(all_dates),
                "temporal_span_days": total_temporal_span,
                "calculated_at": now_utc.isoformat(),
            }
        finally:
            if close_db and db:
                db.close()

    def get_hardened_projection(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Calculates theoretical and observed accumulation projections.
        Strictly labeled PROJECTED and never GUARANTEED (guarantee: False).
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            # Query eligible rows and per-destination depth
            streaks = self.get_destination_streaks(db=db)
            velocity = self.get_accumulation_velocity(db=db)

            dest_list = streaks["destinations"]
            total_eligible = sum(d["eligible_rows"] for d in dest_list)
            min_depth = min((d["eligible_rows"] for d in dest_list), default=0)
            max_depth_needed = max((d["remaining_to_20"] for d in dest_list), default=0)

            remaining_total_rows = max(0, GATE_MIN_ROWS - total_eligible)
            remaining_per_dest = {d["destination"]: d["remaining_to_20"] for d in dest_list}

            temporal_span = velocity.get("temporal_span_days", 0)
            remaining_temporal_span = max(0, GATE_MIN_TEMPORAL_SPAN_DAYS - temporal_span)

            THEORETICAL_MAX_RATE = 6.0
            theoretical_min_days = math.ceil(max(
                remaining_total_rows / THEORETICAL_MAX_RATE,
                float(max_depth_needed),
                float(remaining_temporal_span)
            ))

            # Observed rate projection
            observed_rate = velocity.get("overall_observed_rate_daily")
            if isinstance(observed_rate, (int, float)) and observed_rate > 0:
                observed_rate_days = math.ceil(max(
                    remaining_total_rows / observed_rate,
                    float(remaining_temporal_span)
                ))
            else:
                observed_rate_days = None

            return {
                "projection_status": "PROJECTED",
                "guarantee": False,
                "label": "MATHEMATICAL_ACCUMULATION_PROJECTION",
                "remaining_total_eligible_rows": remaining_total_rows,
                "remaining_destination_depth": remaining_per_dest,
                "max_remaining_destination_depth": max_depth_needed,
                "remaining_temporal_span_days": remaining_temporal_span,
                "theoretical_maximum_capture_rate": f"{THEORETICAL_MAX_RATE} rows/day (THEORETICAL_MAXIMUM_CAPTURE_RATE)",
                "theoretical_minimum_days": theoretical_min_days,
                "observed_daily_rate": observed_rate,
                "observed_rate_projection_days": observed_rate_days,
                "assumptions": [
                    "All 6 canonical destinations continue to accumulate observations daily.",
                    "No synthetic or fabricated observations are included.",
                    "Existing ProductionEligibilityGate thresholds remain immutable.",
                ],
                "disclaimer": (
                    "This is a mathematical projection under stated operational assumptions. "
                    "It is NOT a guarantee. Actual accumulation depends on legitimate telemetry availability."
                ),
            }
        finally:
            if close_db and db:
                db.close()

    def get_daily_accumulation_health(
        self,
        date_bucket: Optional[str] = None,
        dataset_mode: str = "REAL",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Primary operational endpoint answering:
        "Did today's genuine historical accumulation happen correctly?"

        Reconciles:
        - 6 expected destinations
        - captured observations & ledger records
        - valid, invalid, missing, incomplete, duplicate destinations
        - source health and freshness
        - accumulation velocity and hardened projection
        - authoritative ProductionEligibilityGate verdict
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            now_utc = datetime.now(timezone.utc)
            target_date_str = date_bucket or now_utc.strftime("%Y-%m-%d")

            # 1. Fetch observations for this target date
            obs_query = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.date_bucket == target_date_str,
                HistoricalObservationModel.dataset_mode == dataset_mode.upper().strip(),
            ).all()

            # 2. Fetch ledger entries for this target date
            ledger_query = db.query(DailyCaptureLedgerModel).filter(
                DailyCaptureLedgerModel.date_bucket == target_date_str,
                DailyCaptureLedgerModel.dataset_mode == dataset_mode.upper().strip(),
            ).all()
            ledger_map = {l.destination_id: l for l in ledger_query}

            # Group observations by destination
            obs_by_dest: Dict[str, List[HistoricalObservationModel]] = {}
            for o in obs_query:
                obs_by_dest.setdefault(o.destination_id, []).append(o)

            valid_dests = []
            invalid_dests = []
            missing_dests = []
            incomplete_dests = []
            duplicate_dests = []
            captured_dests = []

            eligible_rows_added = 0
            invalid_rows_added = 0

            sources_attempted_set = set()
            sources_succeeded_set = set()
            sources_failed_list = []

            for dest in CANONICAL_DESTINATIONS:
                records = obs_by_dest.get(dest, [])
                ledger = ledger_map.get(dest)

                # Track sources attempted/succeeded from ledger if available
                if ledger:
                    if ledger.sources_attempted_json:
                        sources_attempted_set.update(ledger.sources_attempted_json)
                    if ledger.sources_succeeded_json:
                        sources_succeeded_set.update(ledger.sources_succeeded_json)
                    if ledger.sources_failed_json:
                        sources_failed_list.extend(ledger.sources_failed_json)

                if len(records) == 0:
                    missing_dests.append(dest)
                elif len(records) > 1:
                    duplicate_dests.append(dest)
                    captured_dests.append(dest)
                else:
                    rec = records[0]
                    captured_dests.append(dest)
                    q = observation_quality_scorer.score_observation(rec)
                    grade = q.quality_grade if isinstance(q.quality_grade, str) else q.quality_grade.value

                    # Track sources from observation provenance
                    prov = rec.signal_provenance_json or {}
                    for sig, p_entry in prov.items():
                        if isinstance(p_entry, dict):
                            src_name = p_entry.get("source")
                            if src_name:
                                sources_attempted_set.add(src_name)
                                if p_entry.get("is_available"):
                                    sources_succeeded_set.add(src_name)

                    if grade == "INVALID":
                        invalid_dests.append(dest)
                        invalid_rows_added += 1
                    elif rec.current_crowd_pressure is None:
                        incomplete_dests.append(dest)
                    else:
                        valid_dests.append(dest)
                        eligible_rows_added += 1

            # Determine Daily Completeness Status
            if len(valid_dests) == len(CANONICAL_DESTINATIONS):
                capture_status = STATUS_FULL_SUCCESS
            elif len(valid_dests) > 0:
                capture_status = STATUS_PARTIAL_SUCCESS
            else:
                capture_status = STATUS_FAILED

            # Fetch sub-service metrics
            source_health = self.get_source_health(db=db)
            destination_streaks = self.get_destination_streaks(db=db)
            velocity = self.get_accumulation_velocity(db=db)
            projection = self.get_hardened_projection(db=db)

            # Latest successful capture timestamp across real observations
            latest_real = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == "REAL"
            ).order_by(HistoricalObservationModel.observed_at.desc()).first()
            latest_successful = latest_real.observed_at.isoformat() if latest_real and latest_real.observed_at else None

            # Evaluate against authoritative gate
            from app.services.historical.readiness_service import historical_readiness_service
            readiness_summary = historical_readiness_service.get_readiness_summary(db=db)

            return {
                "status": capture_status,
                "capture_status": capture_status,
                "observation_date": target_date_str,
                "date_bucket": target_date_str,
                "dataset_mode": dataset_mode.upper().strip(),
                "expected_destinations": len(CANONICAL_DESTINATIONS),
                "captured_destinations": captured_dests,
                "captured_count": len(captured_dests),
                "valid_destinations": valid_dests,
                "captured_valid": len(valid_dests),
                "invalid_destinations": invalid_dests,
                "captured_invalid": len(invalid_dests),
                "missing_destinations": missing_dests,
                "missing": len(missing_dests),
                "incomplete_destinations": incomplete_dests,
                "incomplete": len(incomplete_dests),
                "duplicate_destinations": duplicate_dests,
                "duplicates": len(duplicate_dests),
                "eligible_rows_added": eligible_rows_added,
                "invalid_rows_added": invalid_rows_added,
                "sources_attempted": sorted(list(sources_attempted_set)),
                "sources_succeeded": sorted(list(sources_succeeded_set)),
                "sources_failed": sources_failed_list,
                "latest_successful_capture": latest_successful,
                "provenance_status": "AUTHENTIC_TELEMETRY" if len(sources_succeeded_set) > 0 else "NO_TELEMETRY",
                "source_health": source_health,
                "destination_health": destination_streaks.get("destinations", []),
                "velocity": velocity,
                "projection": projection,
                "eligibility": {
                    "eligible": readiness_summary.get("eligible", False),
                    "gate_status": readiness_summary.get("gate_status", "INSUFFICIENT_DATA"),
                    "ml_eligible_real_rows": readiness_summary.get("ml_eligible_real_rows", 0),
                    "required_rows": GATE_MIN_ROWS,
                    "temporal_span_days": readiness_summary.get("temporal_span_days", 0),
                    "required_temporal_span_days": GATE_MIN_TEMPORAL_SPAN_DAYS,
                    "target_availability_percent": readiness_summary.get("target_availability_percent", 100.0),
                    "target_variance": readiness_summary.get("target_variance", 0.0),
                    "core_missingness_percent": readiness_summary.get("core_signal_missingness_percent", 0.0),
                    "failed_requirements": readiness_summary.get("failed_requirements", []),
                },
                "audited_at": now_utc.isoformat(),
            }
        finally:
            if close_db and db:
                db.close()

    def get_accumulation_history(
        self,
        limit_days: int = 14,
        dataset_mode: str = "REAL",
        db: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns chronological daily accumulation health records for the last N dates.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            # Find all distinct observation dates
            dates_query = db.query(HistoricalObservationModel.date_bucket).filter(
                HistoricalObservationModel.dataset_mode == dataset_mode.upper().strip()
            ).distinct().order_by(HistoricalObservationModel.date_bucket.desc()).limit(limit_days).all()

            distinct_dates = [d[0] for d in dates_query if d[0]]

            history = []
            for dt_str in distinct_dates:
                daily_h = self.get_daily_accumulation_health(
                    date_bucket=dt_str,
                    dataset_mode=dataset_mode,
                    db=db,
                )
                history.append({
                    "date": dt_str,
                    "status": daily_h["capture_status"],
                    "expected_destinations": daily_h["expected_destinations"],
                    "captured_valid": daily_h["captured_valid"],
                    "captured_invalid": daily_h["captured_invalid"],
                    "missing": daily_h["missing"],
                    "incomplete": daily_h["incomplete"],
                    "duplicates": daily_h["duplicates"],
                    "eligible_rows_added": daily_h["eligible_rows_added"],
                })

            return history
        finally:
            if close_db and db:
                db.close()


accumulation_health_service = AccumulationHealthService()
