# Yatri Setu — Eligibility Transition Protocol

## Overview

The **Eligibility Transition Protocol** establishes a formal, deterministic, and auditable bridge between **genuine daily observation accumulation** and **first real XGBoost model training and promotion**.

The protocol enforces the immutable `ProductionEligibilityGate` without exceptions, waivers, or relaxed thresholds. Production training of XGBoost forecasting models cannot be triggered until all immutable gate criteria are satisfied.

---

## 1. Immutable Production Gate Criteria

The `ProductionEligibilityGate` is the sole and ultimate authority for production readiness:

| Requirement | Threshold | Current Measured Value | Gate Verdict |
| :--- | :--- | :--- | :--- |
| **Dataset Mode** | `REAL` | `REAL` | **PASS** |
| **Total Rows** | $\ge 180$ | `66` (94 physical, 28 invalid excluded) | **FAIL (66 / 180)** |
| **Distinct Destinations** | $\ge 3$ canonical | `6` (`darjeeling`, `kalimpong`, `mirik`, `lava`, `lolegaon`, `rishop`) | **PASS** |
| **Rows per Destination** | $\ge 20$ for all | `11` for all 6 canonical destinations | **FAIL (11 / 20)** |
| **Temporal Span** | $\ge 30$ calendar days | `38` calendar days | **PASS** |
| **Target Availability** | $100\%$ | $100\%$ | **PASS** |
| **Core Missingness** | $\le 70\%$ | $29.1\%$ | **PASS** |
| **Target Variance** | $\ge 4.0$ | $234.18$ | **PASS** |

**Current Global Eligibility**: `INSUFFICIENT_DATA` (Authoritative baseline `baseline_rule_v2` is retained).

---

## 2. Transition Detection Flow

```
Daily Capture / Accumulation Cycle
                ↓
Data Validation & Quarantine (Invalid Rows Excluded)
                ↓
ProductionEligibilityGate Evaluation
                ↓
Is Gate Verdict == PASS?
       ├── NO  → Remain BASELINE_ACTIVE (State: BASELINE_ACTIVE — INSUFFICIENT_DATA)
       └── YES → Transition Detected:
                 INSUFFICIENT_DATA -> ELIGIBLE
                 (State: BASELINE_ACTIVE — ELIGIBILITY_REACHED)
                        ↓
                 Dataset Fingerprinting (SHA-256)
                        ↓
                 Duplicate Training Check (Skip if fingerprint matches last run)
                        ↓
                 Train Candidate XGBoost Model (22-feature Schema 2.0.0, chronological split)
                        ↓
                 Validate Candidate Artifact & Real Metrics (MAE, RMSE, R²)
                        ↓
                 Compare Against Baseline Rule V2
                        ↓
                 Atomic Promotion (State: XGBOOST_ACTIVE)
                        ↓
                 If Promotion Fails: State -> PROMOTION_FAILED — BASELINE_RETAINED
```

---

## 3. Transition Audit Records

Every state change generates an immutable audit record containing:
- `timestamp`: UTC ISO-8601 timestamp.
- `previous_state`: Prior state machine state.
- `new_state`: Target state machine state.
- `reason`: Structured explanation.
- `eligible_rows`: Total ML-eligible rows at transition time.
- `temporal_span`: Calendar days between earliest and latest observations.
- `destination_depth`: Map of canonical destinations and their respective eligible row counts.
- `target_availability`: Percentage of rows with non-null `current_crowd_pressure`.
- `core_missingness`: Aggregate core telemetry missingness percentage.
- `target_variance`: Variance of historical crowd target.
- `dataset_fingerprint`: 64-character SHA-256 fingerprint.

Transitions are exposed via `GET /api/admin/ml/readiness` and `coordinator.get_readiness_report()["transition_history"]`.

---

## 4. Promotion Safeguards

1. **Gate Invariance**: Zero training without full gate clearance.
2. **Artifact Integrity**: Candidate model is saved to `_candidate.joblib` and thoroughly verified before swap.
3. **Rollback Resilience**: In case of failure or explicit operator request, `rollback_to_baseline()` restores `baseline_rule_v2` immediately without disrupting user forecasts.
4. **Duplicate Training Suppression**: The SHA-256 fingerprint ensures the coordinator never retrains on an unchanged dataset snapshot.
