# Yatri Setu — Production XGBoost Training & Model Promotion Lifecycle (Prompt 6)

> **Mandatory Policy Statement:**  
> **XGBoost production readiness depends on genuine historical data satisfying the existing eligibility gate. Synthetic benchmark performance does not establish real-world forecasting accuracy.**

---

## 1. Lifecycle Architecture & State Machine

Yatri Setu enforces strict isolation between deterministic current-crowd intelligence (Crowd Engine V2) and future crowd forecasting (XGBoost Multi-Horizon Pipeline).

To prevent unvalidated models, synthetic benchmarks, or data-starved candidates from polluting production, every model transitions through explicit lifecycle states managed by [`ProductionTrainingCoordinator`](file:///d:/yatri-setu/backend/app/services/ml/production_training_coordinator.py):

```
                        ┌──────────────────────────────┐
                        │       BASELINE_ACTIVE        │◄─── (Safe Fallback / Cold Start)
                        └──────────────┬───────────────┘
                                       │
                        [Evaluate Real Dataset via Gate]
                                       │
                   ┌───────────────────┴───────────────────┐
                   │                                       │
            [Ineligible]                              [Eligible]
                   │                                       │
                   ▼                                       ▼
        ┌─────────────────────┐               ┌──────────────────────────┐
        │  INSUFFICIENT_DATA  │               │   REAL_TRAINING_READY    │
        └─────────────────────┘               └────────────┬─────────────┘
                                                           │
                                             [Atomic Candidate Training]
                                                           │
                                              ┌────────────┴────────────┐
                                              │                         │
                                        [Validation Pass]        [Validation Fail]
                                              │                         │
                                              ▼                         ▼
                                   ┌──────────────────────┐  ┌─────────────────────┐
                                   │REAL_PRODUCTION_ACTIVE│  │   TRAINING_FAILED   │
                                   └──────────────────────┘  └─────────────────────┘
```

### Explicit State Definitions:
1. `BASELINE_ACTIVE`: Current active baseline fallback model (`BaselineRuleModel`). Guaranteed 100% availability, zero ML dependencies.
2. `SYNTHETIC_BENCHMARK`: Model trained exclusively on synthetic multi-seasonal benchmarks (Seed 42). Explicitly marked `production_eligible = False`.
3. `REAL_TRAINING_READY`: Genuine historical dataset has successfully cleared all 8 checks of the `ProductionEligibilityGate`.
4. `REAL_TRAINED`: Candidate model trained on chronological partitions ($T_{\text{train}} < T_{\text{val}} < T_{\text{test}}$) with validation metrics computed.
5. `REAL_PRODUCTION_ACTIVE`: Candidate model passed schema validation (2.0.0, 22 features), directional metrics validation, and was atomically promoted to the active production artifact (`crowd_xgb_v1.joblib`).
6. `TRAINING_FAILED`: Candidate training encountered an error or validation failure; the previous working production model or baseline was safely preserved intact.
7. `INSUFFICIENT_DATA`: Real dataset contains fewer than required rows or days. Training is safely refused without data fabrication.

---

## 2. Production Eligibility Gate Requirements

The [`ProductionEligibilityGate`](file:///d:/yatri-setu/backend/app/services/ml/eligibility_gate.py) enforces 8 mandatory constraints before certifying any dataset:

| Rule Name | Threshold | Description |
| :--- | :--- | :--- |
| `dataset_mode_real` | `dataset_mode == "REAL"` | Strictly prohibits synthetic or mixed datasets from production certification. |
| `min_total_rows` | $\ge 180$ rows | Ensures statistical volume across multi-horizon training pairs. |
| `min_destinations` | $\ge 3$ destinations | Prevents single-destination localized overfitting. |
| `min_rows_per_destination` | $\ge 20$ rows | Enforces cross-circuit balance. |
| `min_temporal_span_days` | $\ge 30$ days | Captures at least one full monthly calendar cycle. |
| `target_availability_100` | $100\%$ | Ground truth target pressure must exist for every training pair. |
| `max_missing_signal_rate` | $\le 70\%$ | Core telemetry signals must have sufficient density. |
| `min_target_variance` | $\ge 4.0$ | Ensures sufficient variance for tree splits. |

---

## 3. Atomic Candidate Training & Promotion Workflow

1. **Gate Inspection**: `ProductionTrainingCoordinator.check_eligibility()` queries all genuine REAL records.
2. **Refusal on Ineligibility**: If the gate fails, returns `status = "INSUFFICIENT_DATA"` with structured diagnostics and failed requirements.
3. **Duplicate Prevention**: If row count and temporal span are unchanged from the last run, returns `status = "NO_NEW_DATA"` without retraining.
4. **Candidate Training**:
   - Saves candidate model to `crowd_xgb_candidate.joblib`.
   - Re-loads candidate artifact to verify disk integrity and schema parity (Schema 2.0.0, 22 features).
   - Generates test set metrics alongside `BaselineRuleModel` benchmark metrics.
5. **Atomic Promotion**:
   - Backs up existing production artifact to `crowd_xgb_backup.joblib`.
   - Atomically moves candidate to `crowd_xgb_v1.joblib`.
   - Re-registers active model in `ModelRegistry`.
   - Records comprehensive training provenance.

---

## 4. Retraining Strategy & API Contracts

- **Endpoint**: `POST /api/admin/ml/retrain-if-eligible`
  - Parameter: `force: bool = False`
  - Safe for cron/scheduler execution.
- **Readiness Endpoint**: `GET /api/admin/ml/production-readiness`
  - Exposes active model status, training provenance, schema version, and eligibility diagnostics.
