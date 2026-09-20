# Real Model Promotion Audit & Authority Report

**Milestone**: Prompt 10 / Branch `v10`  
**System**: Yatri Setu Production Model Registry  
**Document**: Active Production Model Authority, Gate Evaluation Audit, and Rollback Safeguards  

---

## 1. Executive Summary & Active Model Authority

* **Active Production Model**: `baseline_rule_v2` (`BaselineRuleModel`)
* **Active Model Status**: `BASELINE_ACTIVE`
* **Production Eligibility Verdict**: `INSUFFICIENT_DATA` (Gate evaluation = `FAIL`)
* **Candidate Model Status**: `NOT_TRAINED` (Production training blocked by gate)
* **Synthetic Benchmark Status**: `SYNTHETIC_BENCHMARK` (`production_eligible = False`, quarantined)

Per Prompt 10 Non-Negotiable Principle 17:
> **If eligibility remains false, leave the baseline authoritative.**

Because the genuine REAL dataset currently contains 66 ML-eligible observations (requiring 180 rows and 20 rows/destination), the system refuses to manufacture data or weaken thresholds. `baseline_rule_v2` remains the sole authoritative production model.

---

## 2. Production Eligibility Gate Audit (Live Evaluation)

```json
{
  "gate_status": "INSUFFICIENT_DATA",
  "is_eligible": false,
  "dataset_mode": "REAL",
  "total_real_rows": 94,
  "ml_eligible_real_rows": 66,
  "invalid_rows": 28,
  "unique_dates": 11,
  "temporal_span_days": 38,
  "destinations_present": 6,
  "minimum_destination_depth": 11,
  "target_availability": 100.0,
  "core_missingness": 29.1,
  "target_variance": 234.18,
  "requirements_breakdown": {
    "dataset_mode": "PASS",
    "total_rows": "FAIL",
    "temporal_span": "PASS",
    "destinations": "PASS",
    "destination_depth": "FAIL",
    "target_availability": "PASS",
    "core_missingness": "PASS",
    "target_variance": "PASS"
  },
  "failed_requirements": [
    "total_rows (66) < min_rows (180)",
    "min_rows_per_destination (11) < required (20)"
  ],
  "rows_remaining": 114,
  "destination_rows_remaining": 9,
  "days_remaining": 0
}
```

---

## 3. Promotion Criteria Checklist (When Eligible)

When continuous daily accumulation satisfies all gate requirements, candidate promotion is governed by these non-negotiable criteria:

1. [ ] **Gate Certification**: 100% of ProductionEligibilityGate requirements pass.
2. [ ] **Artifact Load Verification**: Candidate model reloads cleanly from disk with valid booster weights.
3. [ ] **Schema Version Compliance**: Feature vector has exactly 22 dimensions conforming to Schema `2.0.0`.
4. [ ] **Chronological Validation**: Validation split strictly follows chronological ordering without future leakage.
5. [ ] **Baseline Superiority**:
   * Candidate $\text{MAE} \le \text{Baseline MAE}$
   * Candidate $R^2 \ge 0.0$
   * Directional accuracy $\ge 60\%$
6. [ ] **Provenance Completeness**: Model metadata links directly to the specific database observations used in training.
7. [ ] **Atomic Swap**: Candidate artifact atomically moves to production position; previous artifact backed up.

If any single check fails, the state transitions to `PROMOTION_REJECTED` or `VALIDATION_FAILED`, and `baseline_rule_v2` is retained.

---

## 4. Rollback Protocol & Operational Safety

In the event of an operational anomaly post-promotion:
1. **Automated Rollback**: If the newly promoted model fails deserialization or produces unhandled exceptions during inference, `ProductionTrainingCoordinator.rollback_to_baseline()` immediately activates.
2. **Backup Artifact Restoration**: The previous production artifact is preserved as `crowd_xgb_v1_backup.joblib` and can be restored in-place.
3. **Audit Trail**: Every promotion and rollback event records timestamp, reason, dataset fingerprint, and operational metadata.
