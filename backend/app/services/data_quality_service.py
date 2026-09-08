"""
Data Quality Pipeline Service (Milestone 6A).
Performs comprehensive data auditing on the historical crowd observation dataset,
evaluating missing values, duplicate records, range constraints, date continuity,
and destination integrity.
"""

from datetime import datetime, date
from typing import List, Dict, Set, Optional, Tuple
from app.models.dataset_evaluation import (
    HistoricalObservation,
    DataQualityReport,
    DataQualityCheckResult
)
from app.data.historical_dataset import get_historical_dataset, DESTINATIONS


VALID_DESTINATIONS: Set[str] = set(DESTINATIONS)
SIGNAL_FIELDS = [
    "historical_footfall",
    "accommodation_occupancy",
    "booking_demand",
    "search_demand",
    "event_pressure",
    "holiday_pressure",
    "weather_pressure",
    "traffic_pressure",
]


class DataQualityService:
    """
    Automated data quality validation engine.
    Audits incoming and historical crowd observation datasets before model ingestion.
    """

    def validate_dataset(
        self,
        dataset: Optional[List[HistoricalObservation]] = None
    ) -> DataQualityReport:
        """
        Runs full suite of 6 integrity checks and generates a structured DataQualityReport.
        """
        if dataset is None:
            dataset = get_historical_dataset()

        total_records = len(dataset)
        if total_records == 0:
            return DataQualityReport(
                dataset_mode="SYNTHETIC DEMO",
                total_records=0,
                destinations_count=0,
                date_range={"start": "N/A", "end": "N/A", "days_covered": "0"},
                completeness_score=0.0,
                quality_rating="DEGRADED",
                checks=[
                    DataQualityCheckResult(
                        name="empty_dataset_check",
                        passed=False,
                        detail="Dataset contains 0 records",
                        anomalies_detected=1
                    )
                ],
                is_valid=False,
                summary="Dataset is empty. Zero records available for analysis."
            )

        checks: List[DataQualityCheckResult] = []
        anomalies_total = 0

        # Check 1: Missing Values Check
        missing_count = 0
        for obs in dataset:
            for field in ["date", "destination_id", "observed_pressure"] + SIGNAL_FIELDS:
                val = getattr(obs, field, None)
                if val is None:
                    missing_count += 1

        checks.append(
            DataQualityCheckResult(
                name="missing_values_audit",
                passed=(missing_count == 0),
                detail="All required fields present with zero null values" if missing_count == 0 else f"{missing_count} missing field instances detected",
                anomalies_detected=missing_count
            )
        )
        anomalies_total += missing_count

        # Check 2: Signal Bounds Check (0.0 <= val <= 100.0)
        signal_out_of_bounds = 0
        for obs in dataset:
            for field in SIGNAL_FIELDS:
                val = getattr(obs, field, 0.0)
                if val < 0.0 or val > 100.0:
                    signal_out_of_bounds += 1

        checks.append(
            DataQualityCheckResult(
                name="signal_range_audit",
                passed=(signal_out_of_bounds == 0),
                detail="All 8 intelligence signals strictly bounded between 0.0 and 100.0" if signal_out_of_bounds == 0 else f"{signal_out_of_bounds} signal readings outside [0, 100]",
                anomalies_detected=signal_out_of_bounds
            )
        )
        anomalies_total += signal_out_of_bounds

        # Check 3: Observed Pressure Bounds Check (0.0 <= val <= 100.0)
        target_out_of_bounds = sum(1 for obs in dataset if obs.observed_pressure < 0.0 or obs.observed_pressure > 100.0)
        checks.append(
            DataQualityCheckResult(
                name="target_range_audit",
                passed=(target_out_of_bounds == 0),
                detail="All observed ground-truth pressure readings within [0.0, 100.0]" if target_out_of_bounds == 0 else f"{target_out_of_bounds} observed pressure values outside [0, 100]",
                anomalies_detected=target_out_of_bounds
            )
        )
        anomalies_total += target_out_of_bounds

        # Check 4: Duplicate Record Check (unique destination_id + date)
        seen_keys: Set[Tuple[str, str]] = set()
        duplicates_count = 0
        for obs in dataset:
            key = (obs.destination_id.lower().strip(), obs.date)
            if key in seen_keys:
                duplicates_count += 1
            else:
                seen_keys.add(key)

        checks.append(
            DataQualityCheckResult(
                name="duplicate_records_audit",
                passed=(duplicates_count == 0),
                detail="Zero duplicate records found; (destination_id, date) is strictly unique" if duplicates_count == 0 else f"{duplicates_count} duplicate (destination, date) pairs found",
                anomalies_detected=duplicates_count
            )
        )
        anomalies_total += duplicates_count

        # Check 5: Destination Identifier Integrity
        invalid_dest_count = sum(1 for obs in dataset if obs.destination_id.lower().strip() not in VALID_DESTINATIONS)
        checks.append(
            DataQualityCheckResult(
                name="destination_id_audit",
                passed=(invalid_dest_count == 0),
                detail="All records map to registered circuit destinations" if invalid_dest_count == 0 else f"{invalid_dest_count} records have unknown destination IDs",
                anomalies_detected=invalid_dest_count
            )
        )
        anomalies_total += invalid_dest_count

        # Check 6: Date Ordering & Continuity Audit
        by_dest: Dict[str, List[str]] = {}
        for obs in dataset:
            by_dest.setdefault(obs.destination_id.lower().strip(), []).append(obs.date)

        date_order_issues = 0
        for dest, dates in by_dest.items():
            for i in range(1, len(dates)):
                if dates[i] <= dates[i - 1]:
                    date_order_issues += 1

        checks.append(
            DataQualityCheckResult(
                name="chronological_continuity_audit",
                passed=(date_order_issues == 0),
                detail="Strict chronological sequence verified with no date regressions" if date_order_issues == 0 else f"{date_order_issues} chronological ordering anomalies detected",
                anomalies_detected=date_order_issues
            )
        )
        anomalies_total += date_order_issues

        # Summarize dates & destinations
        all_dates = sorted(list({obs.date for obs in dataset}))
        all_dests = sorted(list({obs.destination_id for obs in dataset}))

        start_d = all_dates[0] if all_dates else "N/A"
        end_d = all_dates[-1] if all_dates else "N/A"
        days_covered = len(all_dates)

        completeness_pct = max(0.0, min(100.0, round(((total_records - (anomalies_total / 8.0)) / total_records) * 100.0, 2)))
        all_passed = all(c.passed for c in checks)

        if all_passed and completeness_pct >= 99.0:
            rating = "HIGH"
        elif completeness_pct >= 90.0:
            rating = "MEDIUM"
        elif completeness_pct >= 75.0:
            rating = "LOW"
        else:
            rating = "DEGRADED"

        summary = (
            f"Dataset verified across {total_records} observations ({days_covered} days, {len(all_dests)} destinations). "
            f"Quality status: {rating} ({'All 6 checks passed' if all_passed else f'{anomalies_total} anomalies detected'}). "
            f"Strict synthetic transparency active."
        )

        return DataQualityReport(
            dataset_mode="SYNTHETIC DEMO",
            total_records=total_records,
            destinations_count=len(all_dests),
            date_range={
                "start": start_d,
                "end": end_d,
                "days_covered": str(days_covered)
            },
            completeness_score=completeness_pct,
            quality_rating=rating,
            checks=checks,
            is_valid=all_passed,
            summary=summary,
            evaluated_at=datetime.utcnow()
        )


data_quality_service = DataQualityService()
