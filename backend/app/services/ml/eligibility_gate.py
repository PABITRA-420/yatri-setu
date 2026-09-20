"""
Production Eligibility Gate for ML Crowd Forecasting Models (Milestone 11 / Prompt 4).

Evaluates whether an observation dataset possesses sufficient genuine historical observations,
temporal span, cross-destination representation, and signal quality to be certified as
a PRODUCTION_READY forecasting model.

Rules:
- Synthetic benchmark datasets (Seed 42) are NEVER production eligible.
- Mixed datasets are classified as MIXED_BENCHMARK and are not production eligible.
- Real datasets with insufficient observations fail the gate with INSUFFICIENT_DATA
  and provide a detailed audit checklist without fabricating data.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class ProductionEligibilityRules:
    """Configurable thresholds for certifying ML production eligibility."""
    min_total_rows: int = 180
    min_rows_per_destination: int = 20
    min_destinations: int = 3
    min_temporal_span_days: int = 30
    max_missing_signal_rate: float = 0.70
    min_target_variance: float = 4.0
    require_real_dataset_mode: bool = True


@dataclass
class EligibilityCheckItem:
    rule_name: str
    passed: bool
    observed_value: Any
    threshold: Any
    detail: str


@dataclass
class ProductionEligibilityVerdict:
    is_eligible: bool
    status: str  # PRODUCTION_READY | INSUFFICIENT_DATA | SYNTHETIC_BENCHMARK | MIXED_BENCHMARK
    checks: List[EligibilityCheckItem] = field(default_factory=list)
    failure_reasons: List[str] = field(default_factory=list)
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    notes: str = ""
    dataset_mode: str = "REAL"
    total_rows: int = 0
    distinct_destinations: int = 0
    temporal_span_days: int = 0
    target_availability_percent: float = 0.0
    core_signal_missingness_percent: float = 0.0
    target_variance: float = 0.0
    requirements: Dict[str, Any] = field(default_factory=dict)
    failed_requirements: List[str] = field(default_factory=list)

    @property
    def eligible(self) -> bool:
        return self.is_eligible

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eligible": self.is_eligible,
            "is_eligible": self.is_eligible,
            "status": self.status,
            "dataset_mode": self.dataset_mode,
            "total_rows": self.total_rows,
            "distinct_destinations": self.distinct_destinations,
            "temporal_span_days": self.temporal_span_days,
            "target_availability_percent": self.target_availability_percent,
            "core_signal_missingness_percent": self.core_signal_missingness_percent,
            "target_variance": self.target_variance,
            "requirements": self.requirements,
            "failed_requirements": self.failed_requirements,
            "failure_reasons": self.failure_reasons,
            "checks": [
                {
                    "rule": c.rule_name,
                    "passed": c.passed,
                    "observed": c.observed_value,
                    "threshold": c.threshold,
                    "detail": c.detail,
                }
                for c in self.checks
            ],
            "evaluated_at": self.evaluated_at.isoformat(),
            "notes": self.notes,
        }

    def to_structured_diagnostics(self) -> Dict[str, Any]:
        return {
            "eligible": self.is_eligible,
            "dataset_mode": self.dataset_mode,
            "total_rows": self.total_rows,
            "distinct_destinations": self.distinct_destinations,
            "temporal_span_days": self.temporal_span_days,
            "target_availability_percent": self.target_availability_percent,
            "core_signal_missingness_percent": self.core_signal_missingness_percent,
            "target_variance": self.target_variance,
            "requirements": self.requirements,
            "failed_requirements": self.failed_requirements,
        }


class ProductionEligibilityGate:
    """Evaluates dataset readiness before training or model promotion."""

    def __init__(self, rules: Optional[ProductionEligibilityRules] = None):
        self.rules = rules or ProductionEligibilityRules()

    def evaluate(
        self,
        features: List[Dict[str, Any]],
        targets: List[float],
        destinations: List[str],
        dataset_mode: str = "REAL",
        date_range: Optional[Dict[str, str]] = None,
    ) -> ProductionEligibilityVerdict:
        checks: List[EligibilityCheckItem] = []
        failure_reasons: List[str] = []
        failed_requirements: List[str] = []

        clean_mode = dataset_mode.upper().strip()
        total_rows = len(features)
        dest_count = len(destinations)

        # Calculate target availability
        target_avail_pct = 100.0 if (targets and len(targets) == total_rows and total_rows > 0) else (
            round((len(targets) / max(1, total_rows)) * 100.0, 1) if total_rows > 0 else 0.0
        )

        # Calculate timespan
        span_days = 0
        if date_range and date_range.get("start") and date_range.get("end"):
            try:
                d1 = datetime.strptime(date_range["start"], "%Y-%m-%d").date()
                d2 = datetime.strptime(date_range["end"], "%Y-%m-%d").date()
                span_days = max(0, (d2 - d1).days + 1)
            except Exception:
                span_days = 0

        # Calculate core missingness
        core_signals = [
            "booking_demand", "search_demand", "event_pressure",
            "holiday_pressure", "weather_pressure", "traffic_pressure"
        ]
        total_slots = max(1, total_rows * len(core_signals))
        missing_count = sum(
            1 for row in features
            for sig in core_signals
            if row.get(sig) is None
        )
        missing_rate = round(missing_count / total_slots, 4)
        missing_pct = round(missing_rate * 100.0, 1)

        # Target variance
        target_var = round(float(np.var(targets)), 3) if targets and len(targets) > 1 else 0.0

        requirements_dict = {
            "min_rows": self.rules.min_total_rows,
            "min_destinations": self.rules.min_destinations,
            "min_rows_per_destination": self.rules.min_rows_per_destination,
            "min_days": self.rules.min_temporal_span_days,
            "target_availability": 100,
            "max_core_missingness": int(self.rules.max_missing_signal_rate * 100),
            "min_target_variance": self.rules.min_target_variance,
        }

        # Check 1: Dataset mode certification
        is_real = clean_mode == "REAL"
        checks.append(
            EligibilityCheckItem(
                rule_name="dataset_mode_real",
                passed=is_real,
                observed_value=clean_mode,
                threshold="REAL",
                detail=(
                    "Dataset is genuine REAL historical observations."
                    if is_real else
                    f"Dataset mode '{clean_mode}' is not real historical data."
                ),
            )
        )
        if not is_real:
            status = "SYNTHETIC_BENCHMARK" if clean_mode == "SYNTHETIC" else "MIXED_BENCHMARK"
            fail_msg = f"Dataset mode is '{clean_mode}'. Only genuine REAL observations can be certified PRODUCTION_READY."
            failure_reasons.append(fail_msg)
            failed_requirements.append(f"dataset_mode ({clean_mode}) != REAL")
            return ProductionEligibilityVerdict(
                is_eligible=False,
                status=status,
                checks=checks,
                failure_reasons=failure_reasons,
                notes="Synthetic and mixed benchmark models are useful for testing and demonstrations, but are ineligible for production certification.",
                dataset_mode=clean_mode,
                total_rows=total_rows,
                distinct_destinations=dest_count,
                temporal_span_days=span_days,
                target_availability_percent=target_avail_pct,
                core_signal_missingness_percent=missing_pct,
                target_variance=target_var,
                requirements=requirements_dict,
                failed_requirements=failed_requirements,
            )

        # Check 2: Minimum total rows
        passed_rows = total_rows >= self.rules.min_total_rows
        checks.append(
            EligibilityCheckItem(
                rule_name="min_total_rows",
                passed=passed_rows,
                observed_value=total_rows,
                threshold=self.rules.min_total_rows,
                detail=f"Total observation rows: {total_rows} (min required: {self.rules.min_total_rows})",
            )
        )
        if not passed_rows:
            failure_reasons.append(
                f"Insufficient observation count: {total_rows} rows < required {self.rules.min_total_rows}."
            )
            failed_requirements.append(f"total_rows ({total_rows}) < min_rows ({self.rules.min_total_rows})")

        # Check 3: Distinct destinations representation
        passed_dests = dest_count >= self.rules.min_destinations
        checks.append(
            EligibilityCheckItem(
                rule_name="min_destinations",
                passed=passed_dests,
                observed_value=dest_count,
                threshold=self.rules.min_destinations,
                detail=f"Destinations covered: {dest_count} (min required: {self.rules.min_destinations})",
            )
        )
        if not passed_dests:
            failure_reasons.append(
                f"Insufficient destination breadth: {dest_count} destinations < required {self.rules.min_destinations}."
            )
            failed_requirements.append(f"distinct_destinations ({dest_count}) < min_destinations ({self.rules.min_destinations})")

        # Check 4: Rows per destination
        dest_row_counts: Dict[str, int] = {}
        for row in features:
            d = row.get("destination_id", "")
            dest_row_counts[d] = dest_row_counts.get(d, 0) + 1

        min_obs_dest = min(dest_row_counts.values()) if dest_row_counts else 0
        passed_per_dest = min_obs_dest >= self.rules.min_rows_per_destination
        checks.append(
            EligibilityCheckItem(
                rule_name="min_rows_per_destination",
                passed=passed_per_dest,
                observed_value=min_obs_dest,
                threshold=self.rules.min_rows_per_destination,
                detail=f"Minimum rows per destination: {min_obs_dest} (min required: {self.rules.min_rows_per_destination})",
            )
        )
        if not passed_per_dest:
            failure_reasons.append(
                f"Destination imbalance: lowest destination has {min_obs_dest} rows < required {self.rules.min_rows_per_destination}."
            )
            failed_requirements.append(f"min_rows_per_destination ({min_obs_dest}) < required ({self.rules.min_rows_per_destination})")

        # Check 5: Temporal span
        passed_span = span_days >= self.rules.min_temporal_span_days
        checks.append(
            EligibilityCheckItem(
                rule_name="min_temporal_span_days",
                passed=passed_span,
                observed_value=span_days,
                threshold=self.rules.min_temporal_span_days,
                detail=f"Observation timespan: {span_days} days (min required: {self.rules.min_temporal_span_days})",
            )
        )
        if not passed_span:
            failure_reasons.append(
                f"Insufficient temporal span: {span_days} days < required {self.rules.min_temporal_span_days} days."
            )
            failed_requirements.append(f"temporal_span_days ({span_days}) < min_days ({self.rules.min_temporal_span_days})")

        # Check 6: Missing value rate across core signals
        passed_missing = missing_rate <= self.rules.max_missing_signal_rate
        checks.append(
            EligibilityCheckItem(
                rule_name="max_missing_signal_rate",
                passed=passed_missing,
                observed_value=missing_rate,
                threshold=self.rules.max_missing_signal_rate,
                detail=f"Missing signal rate: {missing_pct}% (max allowed: {self.rules.max_missing_signal_rate * 100:.1f}%)",
            )
        )
        if not passed_missing:
            failure_reasons.append(
                f"Excessive signal missingness: {missing_pct}% > allowed {self.rules.max_missing_signal_rate * 100:.1f}%."
            )
            failed_requirements.append(f"core_signal_missingness ({missing_pct}%) > max_allowed ({int(self.rules.max_missing_signal_rate * 100)}%)")

        # Check 7: Target variance
        passed_var = target_var >= self.rules.min_target_variance
        checks.append(
            EligibilityCheckItem(
                rule_name="min_target_variance",
                passed=passed_var,
                observed_value=target_var,
                threshold=self.rules.min_target_variance,
                detail=f"Target variance: {target_var:.2f} (min required: {self.rules.min_target_variance})",
            )
        )
        if not passed_var:
            failure_reasons.append(
                f"Insufficient target variation: variance {target_var:.2f} < required {self.rules.min_target_variance}."
            )
            failed_requirements.append(f"target_variance ({target_var}) < min_variance ({self.rules.min_target_variance})")

        # Check 8: Target availability (100%)
        passed_target_avail = (target_avail_pct == 100.0 and total_rows > 0)
        checks.append(
            EligibilityCheckItem(
                rule_name="target_availability_100",
                passed=passed_target_avail,
                observed_value=target_avail_pct,
                threshold=100.0,
                detail=f"Target availability: {target_avail_pct}% (min required: 100.0%)",
            )
        )
        if not passed_target_avail:
            failure_reasons.append(
                f"Target ground truth missing: {target_avail_pct}% < required 100.0%."
            )
            failed_requirements.append(f"target_availability ({target_avail_pct}%) < 100%")

        all_passed = all(c.passed for c in checks)
        status = "PRODUCTION_READY" if all_passed else "INSUFFICIENT_DATA"

        return ProductionEligibilityVerdict(
            is_eligible=all_passed,
            status=status,
            checks=checks,
            failure_reasons=failure_reasons,
            notes=(
                "All production eligibility criteria satisfied. Model is eligible for production deployment."
                if all_passed else
                "Real historical dataset does not yet satisfy production thresholds. Model is held in INSUFFICIENT_DATA status."
            ),
            dataset_mode=clean_mode,
            total_rows=total_rows,
            distinct_destinations=dest_count,
            temporal_span_days=span_days,
            target_availability_percent=target_avail_pct,
            core_signal_missingness_percent=missing_pct,
            target_variance=target_var,
            requirements=requirements_dict,
            failed_requirements=failed_requirements,
        )


production_eligibility_gate = ProductionEligibilityGate()
