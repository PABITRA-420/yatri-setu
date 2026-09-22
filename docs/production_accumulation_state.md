# Production Historical Data Accumulation State & Lifecycle Specification

**Milestone**: Prompt 10 / Branch `v10`  
**System**: Yatri Setu Production Historical Telemetry Accumulation Foundation  
**Document**: Accumulation State Machine, Continuous Ingestion Cadence, and Audit Trail  

---

## 1. Executive Summary & Core Principle

The Yatri Setu continuous accumulation engine operates under an immutable governing rule:
> **Real observations are accumulated organically through daily automated capture and verified first-party transactions. The system NEVER manufactures fake rows, duplicate entries, or synthetic data merely to cross the ProductionEligibilityGate.**

If the gate is not satisfied, the state machine honestly maintains `INSUFFICIENT_DATA`, blocking production XGBoost training and preserving `baseline_rule_v2` as authoritative.

---

## 2. Accumulation State Machine Architecture

The lifecycle follows a deterministic finite-state transition model:

```text
                  ┌──────────────────────────────┐
                  │         ACCUMULATING         │
                  │   (Continuous Daily Capture) │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────┐
                  │          GATE_CHECK          │
                  │  (ProductionEligibilityGate) │
                  └──────────────┬───────────────┘
                                 │
                ┌────────────────┴────────────────┐
                ▼                                 ▼
   ┌───────────────────────────┐    ┌───────────────────────────┐
   │     INSUFFICIENT_DATA     │    │         ELIGIBLE          │
   │   (Rows < 180 or          │    │   (All 8 Criteria Met:    │
   │    Depth < 20 / dest)     │    │    Real, >=180, >=30d,    │
   │  → BASELINE_ACTIVE        │    │    >=3 dests, >=20/dest,  │
   │     authoritative         │    │    100% target, var>=4)   │
   └───────────────────────────┘    └─────────────┬─────────────┘
                                                  │
                                                  ▼
                                    ┌───────────────────────────┐
                                    │         TRAINING          │
                                    │  (Chronological Splits,   │
                                    │   Schema 2.0.0, 22 feats) │
                                    └─────────────┬─────────────┘
                                                  │
                                                  ▼
                                    ┌───────────────────────────┐
                                    │        VALIDATING         │
                                    │ (Artifact Reload, Schema, │
                                    │  Per-Horizon Real Metrics)│
                                    └─────────────┬─────────────┘
                                                  │
                                                  ▼
                                    ┌───────────────────────────┐
                                    │      PROMOTION_CHECK      │
                                    │  (Candidate MAE vs        │
                                    │   Baseline Rule MAE)      │
                                    └───────┬───────────┬───────┘
                                            │           │
                       Candidate Outperforms│           │Candidate Worse
                                            ▼           ▼
   ┌──────────────────────────────────────────┐    ┌───────────────────────────┐
   │          REAL_PRODUCTION_ACTIVE          │    │    PROMOTION_REJECTED     │
   │  (Atomic Promotion, Backup Preserved,    │    │  (Candidate Deleted,      │
   │   Telemetry Provenance Attached)         │    │   BASELINE_ACTIVE         │
   │                                          │    │   Retained Uncorrupted)   │
   └──────────────────────────────────────────┘    └───────────────────────────┘
```

### Safe Failure Fallback Transitions:
* `TRAINING_FAILED`: Candidate cleaned up; active model remains `BASELINE_ACTIVE`.
* `VALIDATION_FAILED`: Schema mismatch or artifact corruption caught; active model remains `BASELINE_ACTIVE`.
* `PROMOTION_REJECTED`: Candidate fails to beat baseline MAE; active model remains `BASELINE_ACTIVE`.
* `ROLLBACK_REQUESTED`: If promoted model encounters operational errors, registry atomically reverts to backup artifact or `baseline_rule_v2`.

---

## 3. Current Live Dataset State (Audited Post-Capture)

| Metric | Current Value | Required Threshold | Status |
| :--- | :---: | :---: | :---: |
| **Total Real Physical Rows** | **94** | N/A (Storage audit) | Audited |
| **ML-Eligible Real Rows** | **66** | $\ge 180$ | **FAIL (114 remaining)** |
| **Invalid Audit Records** | **28** | Quarantined from ML | Isolated |
| **Unique Observation Dates** | **11** | $\ge 30\text{ days span}$ | **PASS** |
| **Temporal Span** | **38 days** | $\ge 30\text{ days}$ | **PASS** |
| **Canonical Destinations Present**| **6 of 6** | $\ge 3$ | **PASS** |
| **Minimum Destination Depth** | **11 rows/dest** | $\ge 20\text{ rows/dest}$ | **FAIL (9 remaining)** |
| **Target Ground-Truth Availability** | **100.0%** | $100.0\%$ | **PASS** |
| **Core Signal Missingness** | **29.1%** | $\le 70.0\%$ | **PASS** |
| **Target Variance ($\sigma^2$)** | **234.18** | $\ge 4.0$ | **PASS** |
| **Dataset Mode** | `REAL` | `REAL` | **PASS** |
| **Duplicate Rows Count** | **0** | $0$ | **PASS** |

### Rows by Destination Breakdown:
* **Darjeeling**: 11 rows
* **Kalimpong**: 11 rows
* **Mirik**: 11 rows
* **Lava**: 11 rows
* **Lolegaon**: 11 rows
* **Rishop**: 11 rows

---

## 4. Daily Scheduled Capture Workflow & Hardening

* **Scheduled Ingestion Method**: `historical_ingestion_service.run_daily_scheduled_capture(date_bucket, dataset_mode="REAL")`
* **Idempotency**: Composite unique constraint `uq_dest_date_bucket_mode` prevents multiple records for the same destination-date bucket. Re-running capture on the same date increments `duplicates_prevented` and updates signals in-place without dirty writes.
* **Failure Tolerance & Missing Telemetry**:
  * Unmeasured historical sensors (promenade footfall turnstiles, historical arterial cameras, historical weather stations) remain strictly `NULL` with `UNAVAILABLE` provider mode.
  * Individual provider failures do not fail the entire batch or synthesize fake proxy data.
* **Duplicate Retraining Prevention**:
  A deterministic SHA-256 fingerprint of the dataset snapshot (`dataset_fingerprint`) prevents redundant retraining runs when no new observations have accumulated.

---

## 5. Structural Accumulation Projection

* **Projection Label**: `STRUCTURAL ACCUMULATION PROJECTION`
* **Disclaimer**:
  > *"This is a data accumulation projection, not a prediction of model accuracy. Structural data projection only. Does not guarantee ML model accuracy or forecast skill upon reaching eligibility."*
* **Observed Daily Accumulation Rate**: 1.74 rows/day (or 6 rows/day under active 6-destination capture cadence).
* **Rows Remaining**: 114 rows.
* **Estimated Calendar Days to Gate Ready**: ~19-20 days of daily continuous capture across all 6 destinations (6 dests $\times$ 19 days = 114 rows).
* **Estimated Projected Date**: November 26, 2026 (at historical single-row rate) or October 10, 2026 (at daily 6-destination capture cadence).
