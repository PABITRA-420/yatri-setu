# Yatri Setu — First Real XGBoost Training Runbook

## Scope & Target Audience

This runbook guides operators, automated jobs, and ML engineers during the automated transition from `BaselineRuleModel` (`baseline_rule_v2`) to the first production-promoted genuine `XGBoostCrowdModel` (`v2.0.0`).

---

## 1. Prerequisites Checklist

Before any production XGBoost model can be trained and promoted, all items below must be verified:

1. **Gate Clearance**:
   - `ProductionEligibilityGate.evaluate().is_eligible == True`
   - Real ML-eligible rows $\ge 180$ (Current: 66)
   - Real rows per destination $\ge 20$ for all 6 destinations (Current: 11)
   - Temporal span $\ge 30$ calendar days (Current: 38)
   - Target availability $= 100\%$ (Current: 100%)
   - Core missingness $\le 70\%$ (Current: 29.1%)
   - Target variance $\ge 4.0$ (Current: 234.18)
2. **Zero Contamination**:
   - Zero synthetic rows in REAL dataset mode.
   - Zero quarantined INVALID rows in training split.
   - Zero duplicated rows.
3. **Pipeline Integrity**:
   - 22-dimensional canonical feature schema (`SCHEMA_VERSION = "2.0.0"`).
   - Strict chronological train/validation/test ordering (no temporal leakage).
   - Multi-horizon forecasting support: $H \in \{1, 3, 7, 14\}$ days.

---

## 2. Automated Execution Procedure

When daily accumulation crosses the gate, the automated cycle (`POST /api/admin/ml/accumulation-cycle` or scheduled cron) executes:

1. **Daily Capture**: Ingests IST calendar day observations across Darjeeling, Kalimpong, Mirik, Lava, Lolegaon, and Rishop.
2. **Gate Re-evaluation**: If ineligible, retains baseline and returns diagnostic state `BASELINE_ACTIVE — INSUFFICIENT_DATA`.
3. **Transition Trigger**: When eligible, detects state transition to `BASELINE_ACTIVE — ELIGIBILITY_REACHED`.
4. **Fingerprinting**: Computes 64-char SHA-256 dataset fingerprint. If previously trained, exits early with `NO_NEW_DATA`.
5. **Candidate Training**: State advances to `TRAINING_IN_PROGRESS`. Trains candidate model and writes to `models/xgboost_crowd_v2.0.0_candidate.joblib`.
6. **Candidate Verification**: State advances to `CANDIDATE_READY`. Evaluates genuine test metrics (MAE, RMSE, R²).
7. **Baseline Comparison**: Compares candidate test MAE/RMSE against `baseline_rule_v2` on the identical test split. State advances to `PROMOTION_PENDING`.
8. **Atomic Promotion**: Backs up previous model to `_backup.joblib`, replaces active model with candidate, and promotes state to `XGBOOST_ACTIVE`.

---

## 3. Manual Verification & Health Checks

Verify the promoted state via backend administrative endpoints:

```bash
# Check production readiness and state machine status
curl -s http://localhost:8000/api/admin/ml/readiness | jq .

# Check destination depth
curl -s http://localhost:8000/api/admin/ml/destination-depth | jq .

# Check accumulation readiness
curl -s http://localhost:8000/api/admin/ml/accumulation-readiness | jq .
```

Expected response after genuine promotion:
- `"model_status": "REAL_PRODUCTION_ACTIVE"`
- `"state_machine_state": "XGBOOST_ACTIVE"`
- `"production_eligible": true`
- `"active_model_name": "xgboost_crowd_v2.0.0"`

---

## 4. Emergency Rollback Protocol

If anomaly, drift, or latency degradation is observed after promotion:

```bash
# Trigger immediate rollback via API
curl -X POST http://localhost:8000/api/admin/ml/rollback \
  -H "Content-Type: application/json" \
  -d '{"reason": "Operator requested emergency rollback"}'
```

Result:
- State switches to `ROLLBACK — BASELINE_ACTIVE`.
- `BaselineRuleModel` (`baseline_rule_v2`) becomes immediately active.
- Prediction endpoints experience zero downtime and zero schema degradation.
