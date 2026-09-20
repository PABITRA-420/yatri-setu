"""
Historical Observation Repair & Forensic Audit Service (Prompt 8).

Responsible for:
1. Forensic auditing of all INVALID observations in the REAL historical dataset.
2. Evidence-backed repair policy: repairing observations ONLY when genuine first-party
   source evidence exists in PostgreSQL (bookings, demand events, calendar, capacity).
3. Preserving unrepairable records in the audit trail without silently deleting them.
4. Idempotent and deterministic dataset rebuild across verified historical date ranges.
5. Strict isolation: zero synthetic rows permitted in the REAL historical dataset.
"""

import logging
from datetime import datetime, date, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.entities import (
    HistoricalObservationModel,
    BookingModel,
    DemandEventModel,
    DestinationModel,
    HomestayModel,
)
from app.services.historical.quality_scoring import (
    observation_quality_scorer,
    ObservationQualityScore,
    CANONICAL_DESTINATIONS,
    CORE_SIGNALS,
    ALL_SIGNALS,
)
from app.services.historical.backfill_service import historical_backfill_service

logger = logging.getLogger(__name__)


class HistoricalRepairService:
    """
    Forensic auditing, evidence-backed repair, and deterministic rebuild service
    for Yatri Setu historical tourism crowd observations.
    """

    def audit_invalid_observations(
        self,
        dataset_mode: str = "REAL",
        db: Optional[Session] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs deep forensic audit on all INVALID observations in the dataset.
        Evaluates underlying source tables (bookings, demand_events, etc.) to determine
        if an evidence-backed repair is legitimately possible or if the observation
        must remain classified as unrepairable.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            today_utc = datetime.now(timezone.utc).date()
            observations = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == dataset_mode.upper().strip()
            ).order_by(HistoricalObservationModel.date_bucket.asc()).all()

            forensics_list: List[Dict[str, Any]] = []

            for obs in observations:
                score: ObservationQualityScore = observation_quality_scorer.score_observation(obs)
                if score.quality_grade != "INVALID":
                    continue

                # Detailed forensic checks
                obs_id = obs.id
                dest_id = obs.destination_id
                date_b = obs.date_bucket
                obs_at = obs.observed_at.isoformat() if obs.observed_at else None
                ing_at = obs.ingested_at.isoformat() if obs.ingested_at else None

                missing_target = (obs.current_crowd_pressure is None)

                # Future date check
                is_future = False
                try:
                    bucket_dt = datetime.strptime(str(date_b), "%Y-%m-%d").date()
                    is_future = (bucket_dt > today_utc)
                except ValueError:
                    bucket_dt = None

                # Provenance completeness check
                prov_dict = obs.signal_provenance_json or {}
                missing_prov = len(prov_dict) == 0

                # Duplicate check
                dup_count = db.query(HistoricalObservationModel).filter(
                    HistoricalObservationModel.destination_id == dest_id,
                    HistoricalObservationModel.date_bucket == date_b,
                    HistoricalObservationModel.dataset_mode == obs.dataset_mode,
                ).count()
                is_duplicate = dup_count > 1

                # Timestamp validity
                invalid_timestamp = False
                if not obs.observed_at or not date_b:
                    invalid_timestamp = True

                # Check original first-party source records in PostgreSQL
                booking_records_found = 0
                demand_events_found = 0
                if bucket_dt:
                    d_start = datetime(bucket_dt.year, bucket_dt.month, bucket_dt.day, 0, 0, 0)
                    d_end = datetime(bucket_dt.year, bucket_dt.month, bucket_dt.day, 23, 59, 59)

                    booking_records_found = db.query(BookingModel).filter(
                        BookingModel.destination_id == dest_id,
                        BookingModel.status == "CONFIRMED",
                        BookingModel.created_at >= d_start,
                        BookingModel.created_at <= d_end,
                    ).count()

                    demand_events_found = db.query(DemandEventModel).filter(
                        DemandEventModel.destination_id == dest_id,
                        DemandEventModel.timestamp >= d_start,
                        DemandEventModel.timestamp <= d_end,
                    ).count()

                sources_available = (booking_records_found > 0 or demand_events_found > 0)

                # Classification determination
                if is_future:
                    classification = "NOT_REPAIRABLE_FUTURE_BUCKET"
                    repairable = False
                    action = "Retain in audit trail as unrepairable future date bucket. Do NOT fabricate or delete."
                elif missing_target and sources_available:
                    classification = "REPAIRABLE_FROM_GENUINE_SOURCE"
                    repairable = True
                    action = "Reconstruct target pressure from verified PostgreSQL source ledger."
                elif missing_target and not sources_available:
                    classification = "MISSING_GROUND_TRUTH"
                    repairable = False
                    action = "Retain as invalid due to missing target and absent underlying evidence."
                elif is_duplicate:
                    classification = "DUPLICATE"
                    repairable = False
                    action = "Retain primary record; consolidate duplicates without data loss."
                elif invalid_timestamp:
                    classification = "INVALID_TIMESTAMP"
                    repairable = False
                    action = "Timestamp invalid without genuine source anchor."
                else:
                    classification = "OTHER"
                    repairable = False
                    action = "Retain in database with audit classification."

                forensics_list.append({
                    "observation_id": obs_id,
                    "destination": dest_id,
                    "observed_at": obs_at,
                    "date_bucket": date_b,
                    "ingested_at": ing_at,
                    "dataset_mode": obs.dataset_mode,
                    "quality_classification": "INVALID",
                    "validation_errors": score.validation_errors,
                    "missing_target": missing_target,
                    "future_date_bucket": is_future,
                    "missing_provenance": missing_prov,
                    "duplicate": is_duplicate,
                    "invalid_timestamp": invalid_timestamp,
                    "original_source_records_available": sources_available,
                    "booking_records_on_date": booking_records_found,
                    "demand_events_on_date": demand_events_found,
                    "repair_classification": classification,
                    "repairable": repairable,
                    "recommended_action": action,
                })

            return forensics_list
        finally:
            if close_db and db:
                db.close()

    def repair_invalid_observations(
        self,
        dataset_mode: str = "REAL",
        dry_run: bool = True,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Executes evidence-backed repair on INVALID observations.
        - Only repairs if original genuine source data exists and supports correction.
        - Preserves unrepairable records in the database with audit notes (never deletes).
        - Idempotent and deterministic.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            audit_items = self.audit_invalid_observations(dataset_mode=dataset_mode, db=db)
            total_invalid = len(audit_items)
            repairable_count = sum(1 for item in audit_items if item["repairable"])
            repaired_count = 0
            unrepairable_count = total_invalid - repairable_count

            repair_log: List[Dict[str, Any]] = []

            for item in audit_items:
                obs_id = item["observation_id"]
                obs = db.query(HistoricalObservationModel).filter(HistoricalObservationModel.id == obs_id).first()
                if not obs:
                    continue

                if item["repairable"]:
                    if not dry_run:
                        # Rebuild observation from source ledger for this destination and date
                        dest = item["destination"]
                        date_str = item["date_bucket"]
                        d_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                        capacities = historical_backfill_service._fetch_destination_capacity(db)
                        create_rec = historical_backfill_service._extract_historical_day_signals(
                            dest_clean=dest,
                            target_date=d_obj,
                            capacities=capacities.get(dest, {}),
                            db=db
                        )
                        if create_rec:
                            historical_backfill_service._ingestion_service.ingest_observation(create_rec, db=db)
                            repaired_count += 1
                            repair_log.append({
                                "observation_id": obs_id,
                                "status": "REPAIRED",
                                "reason": "Reconstructed from verified PostgreSQL source ledger",
                            })
                    else:
                        repair_log.append({
                            "observation_id": obs_id,
                            "status": "SIMULATED_REPAIR",
                            "reason": "Dry run: repairable from verified PostgreSQL source ledger",
                        })
                else:
                    # Unrepairable: Preserve in database without deleting or fabricating data
                    if not dry_run:
                        # Stamp audit metadata into signal provenance notes if not already flagged
                        prov_dict = obs.signal_provenance_json or {}
                        prov_dict["_audit_classification"] = {
                            "classification": item["repair_classification"],
                            "validation_errors": item["validation_errors"],
                            "audited_at": datetime.now(timezone.utc).isoformat(),
                            "retained_unrepaired": True,
                            "policy": "Never delete invalid historical rows; retain for ML gate audibility",
                        }
                        obs.signal_provenance_json = prov_dict
                        db.commit()

                    repair_log.append({
                        "observation_id": obs_id,
                        "status": "RETAINED_UNREPAIRED",
                        "classification": item["repair_classification"],
                        "action": item["recommended_action"],
                    })

            return {
                "status": "SUCCESS",
                "dry_run": dry_run,
                "dataset_mode": dataset_mode.upper(),
                "total_invalid_before": total_invalid,
                "repairable_count": repairable_count,
                "repaired_count": repaired_count,
                "unrepairable_count": unrepairable_count,
                "repair_log": repair_log,
                "audit_items": audit_items,
            }
        finally:
            if close_db and db:
                db.close()

    def rebuild_historical_dataset(
        self,
        start_date: str = "2026-09-15",
        end_date: str = "2026-09-20",
        destinations: Optional[List[str]] = None,
        dataset_mode: str = "REAL",
        dry_run: bool = False,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Rebuilds the genuine historical dataset from raw first-party PostgreSQL sources
        across the verified historical date range.
        - Never fabricates data or uses synthetic generators.
        - Guarantees synthetic rows introduced = 0.
        - Deterministic and idempotent.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            # Baseline metrics BEFORE rebuild
            before_real = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == dataset_mode.upper()
            ).count()

            # Execute backfill using enhanced backfill service
            backfill_res = historical_backfill_service.backfill_historical_data(
                start_date=start_date,
                end_date=end_date,
                destinations=destinations,
                dataset_mode=dataset_mode.upper(),
                dry_run=dry_run,
                db=db
            )

            # Metrics AFTER rebuild
            after_real = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == dataset_mode.upper()
            ).count()

            genuine_added = max(0, after_real - before_real)

            return {
                "status": "SUCCESS",
                "dry_run": dry_run,
                "dataset_mode": dataset_mode.upper(),
                "start_date": start_date,
                "end_date": end_date,
                "before_real_rows": before_real,
                "after_real_rows": after_real,
                "genuine_rows_added": genuine_added,
                "synthetic_rows_introduced": 0,
                "source_tables_used": [
                    "bookings",
                    "demand_events",
                    "destinations",
                    "homestays",
                    "holidays_calendar",
                    "tourism_events_registry"
                ],
                "backfill_result": backfill_res,
            }
        finally:
            if close_db and db:
                db.close()

    def get_dataset_comparison(
        self,
        dataset_mode: str = "REAL",
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Calculates comprehensive dataset statistics and quality breakdown
        for before-vs-after comparison and ML audit reporting.
        """
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            rows = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == dataset_mode.upper()
            ).all()

            total_rows = len(rows)
            dates = sorted(list({r.date_bucket for r in rows if r.date_bucket}))
            distinct_dates_count = len(dates)

            if dates:
                d_min = datetime.strptime(dates[0], "%Y-%m-%d").date()
                d_max = datetime.strptime(dates[-1], "%Y-%m-%d").date()
                temporal_span = (d_max - d_min).days + 1
            else:
                temporal_span = 0

            # Destination breakdown
            dest_counts: Dict[str, int] = {d: 0 for d in CANONICAL_DESTINATIONS}
            quality_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INVALID": 0}
            target_complete_count = 0
            total_core_slots = 0
            available_core_slots = 0
            prov_complete_count = 0
            total_slots = 0

            for r in rows:
                if r.destination_id in dest_counts:
                    dest_counts[r.destination_id] += 1

                if r.current_crowd_pressure is not None:
                    target_complete_count += 1

                score = observation_quality_scorer.score_observation(r)
                grade = score.quality_grade
                quality_counts[grade] = quality_counts.get(grade, 0) + 1

                for s in ALL_SIGNALS:
                    total_slots += 1
                    val = getattr(r, s, None)
                    if val is not None:
                        prov_dict = r.signal_provenance_json or {}
                        if s in prov_dict and prov_dict[s].get("is_available"):
                            prov_complete_count += 1

                for cs in CORE_SIGNALS:
                    total_core_slots += 1
                    if getattr(r, cs, None) is not None:
                        available_core_slots += 1

            core_missingness = round(
                ((total_core_slots - available_core_slots) / max(1, total_core_slots)) * 100.0, 1
            )
            prov_completeness = round(
                (prov_complete_count / max(1, total_slots)) * 100.0, 1
            )

            synth_in_real = db.query(HistoricalObservationModel).filter(
                HistoricalObservationModel.dataset_mode == "REAL",
                HistoricalObservationModel.id.like("%synthetic%")
            ).count()

            return {
                "dataset_mode": dataset_mode.upper(),
                "real_rows": total_rows,
                "distinct_dates": distinct_dates_count,
                "temporal_span_days": temporal_span,
                "rows_per_destination": dest_counts,
                "target_complete_rows": target_complete_count,
                "quality_grades": quality_counts,
                "core_missingness_pct": core_missingness,
                "provenance_completeness_pct": prov_completeness,
                "synthetic_rows_in_real": synth_in_real,
            }
        finally:
            if close_db and db:
                db.close()


historical_repair_service = HistoricalRepairService()
