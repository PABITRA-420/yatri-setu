# Yatri Setu — Production Training State Machine

## 1. Formal State Definitions

Prompt 11 Section 22 defines the formal lifecycle states of the production forecasting coordinator:

```text
┌────────────────────────────────────────┐
│  BASELINE_ACTIVE — INSUFFICIENT_DATA   │◄──────── (Initial Live State: 66/180 rows)
└──────────────────┬─────────────────────┘
                   │
                   │ ProductionEligibilityGate PASS
                   ▼
┌────────────────────────────────────────┐
│  BASELINE_ACTIVE — ELIGIBILITY_REACHED │
└──────────────────┬─────────────────────┘
                   │
                   │ Dataset fingerprint is new -> Trigger Training
                   ▼
┌────────────────────────────────────────┐
│          TRAINING_IN_PROGRESS          │
└──────────────────┬─────────────────────┘
                   │
                   │ Artifact saved to _candidate.joblib
                   ▼
┌────────────────────────────────────────┐
│            CANDIDATE_READY             │
└──────────────────┬─────────────────────┘
                   │
                   │ Real metrics calculated & verified
                   ▼
┌────────────────────────────────────────┐
│           PROMOTION_PENDING            │
└──────┬──────────────────────────┬──────┘
       │                          │
       │ Baseline Comparison PASS │ Baseline Comparison FAIL / Validation Error
       ▼                          ▼
┌────────────────┐       ┌────────────────────────────────────────┐
│ XGBOOST_ACTIVE │       │   PROMOTION_FAILED — BASELINE_RETAINED │
└──────┬─────────┘       └────────────────────────────────────────┘
       │
       │ Rollback Triggered
       ▼
┌───────────────────────────┐
│ ROLLBACK — BASELINE_ACTIVE │
└───────────────────────────┘
```

---

## 2. State Invariants & Guarantees

1. `BASELINE_ACTIVE — INSUFFICIENT_DATA`:
   - Enforced whenever gate has unmet conditions.
   - Predictions served by deterministic `BaselineRuleModel`.
   - Production eligibility flag is strictly `False`.
2. `BASELINE_ACTIVE — ELIGIBILITY_REACHED`:
   - Gate has passed, but candidate training has not yet started.
   - Baseline remains authoritative until candidate passes all checks.
3. `TRAINING_IN_PROGRESS`:
   - Concurrency-safe lock prevents duplicate parallel training runs.
   - Trains multi-horizon XGBoost candidate using 22 canonical features.
4. `CANDIDATE_READY`:
   - Candidate model artifact is isolated in `_candidate.joblib`.
   - Feature schema v2.0.0 is validated against the registry.
5. `PROMOTION_PENDING`:
   - Candidate evaluation metrics (MAE, RMSE, R²) computed on unseen chronological test split.
   - Compared against baseline rule metrics.
6. `XGBOOST_ACTIVE`:
   - Model promoted atomically to active production status.
   - Active model name is `xgboost_crowd_v2.0.0`.
   - `production_eligible = True`.
7. `PROMOTION_FAILED — BASELINE_RETAINED`:
   - If candidate metrics fail benchmark comparison or schema verification.
   - Zero partial promotion. Baseline remains 100% authoritative.
8. `ROLLBACK — BASELINE_ACTIVE`:
   - Manual or automated rollback restored `BaselineRuleModel`.
   - System remains safe, deterministic, and available.
