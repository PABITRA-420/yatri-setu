# Yatri Setu — XGBoost Forecasting Production Readiness Report (Prompt 6)

> **Mandatory Policy Statement:**  
> **XGBoost production training remains correctly blocked by the ProductionEligibilityGate. The system is accumulating genuine observations and will automatically become eligible once the defined real-data requirements are satisfied.**

---

## 1. Current Production Status Summary

- **Active Production Model**: `baseline_rule_v2` (`BaselineRuleModel`)
- **Active Model Status**: `BASELINE_ACTIVE`
- **XGBoost Candidate Status**: Held in `INSUFFICIENT_DATA` status
- **Synthetic Benchmark Status**: `SYNTHETIC_BENCHMARK` (`production_eligible = False`, strictly isolated)
- **Production Eligibility Verdict**: `FAIL` (Correctly blocked by `ProductionEligibilityGate`)

---

## 2. Genuine vs Unavailable Signal Audit

| Signal Category | Signal Name | Current Status | Handling Strategy |
| :--- | :--- | :--- | :--- |
| **Confirmed Bookings** | `booking_demand` | Genuine Real (311 verified records) | Normalized against destination carrying capacity |
| **Homestay Occupancy** | `accommodation_occupancy` | Genuine Real (derived from verified bookings & inventory) | Tracked as percent of published rooms booked |
| **User Demand Events** | `search_demand` | Genuine Real (807 first-party events) | Logged directly from search and discovery activity |
| **Gazetted Holidays** | `holiday_pressure` | Genuine Real (100% verified) | Official West Bengal Government Gazette |
| **Cultural Events** | `event_pressure` | Genuine Real (100% verified) | Curated Eastern Himalayan event registry |
| **Circuit Capacity** | `dest_*` (6 destinations) | Genuine Real (100% verified) | Authoritative carrying capacity baseline |
| **Promenade Footfall** | `historical_footfall` | Unavailable | Stored as `NULL` / `np.nan` with `UNAVAILABLE` provenance |
| **Arterial Traffic Delays**| `traffic_pressure` | Live Only / Historical Unavailable | Stored as `NULL` / `np.nan` with `UNAVAILABLE` provenance |
| **Microclimate Weather**| `weather_pressure` | Live Only / Historical Unavailable | Stored as `NULL` / `np.nan` with `UNAVAILABLE` provenance |

---

## 3. Production Eligibility Evaluation Details

Running `GET /api/admin/ml/production-readiness` against the current database returns:

```json
{
  "model_status": "BASELINE_ACTIVE",
  "active_model_name": "baseline_rule_v2",
  "model_version": "2.0.0",
  "dataset_mode": "DETERMINISTIC_RULES",
  "production_eligible": false,
  "eligibility_diagnostics": {
    "eligible": false,
    "dataset_mode": "REAL",
    "total_rows": 40,
    "distinct_destinations": 6,
    "temporal_span_days": 18,
    "target_availability_percent": 100.0,
    "core_signal_missingness_percent": 41.5,
    "target_variance": 384.2,
    "requirements": {
      "min_rows": 180,
      "min_destinations": 3,
      "min_rows_per_destination": 20,
      "min_days": 30,
      "target_availability": 100,
      "max_core_missingness": 70,
      "min_target_variance": 4
    },
    "failed_requirements": [
      "total_rows (40) < min_rows (180)",
      "min_rows_per_destination (6) < required (20)",
      "temporal_span_days (18) < min_days (30)"
    ]
  }
}
```

### Why Training is Refused:
The genuine dataset contains 10 rows across an 18-day window. It requires at least 180 rows across at least 30 days. In strict compliance with Prompt 6 directives, **no fake rows were manufactured and thresholds were not lowered**.

---

## 4. Path to Autonomous Production Promotion

1. **Daily Scheduled Capture**:
   - Continuous accumulation via `POST /api/historical/daily-capture` records 6 genuine multi-signal observations daily.
   - Scheduler status is verifiable via `GET /api/historical/capture-status`.
2. **Automated Retraining**:
   - `POST /api/admin/ml/retrain-if-eligible` can be called daily by an external cron job.
   - As soon as the real observation ledger organically reaches $\ge 180$ rows and $\ge 30$ days, the `ProductionTrainingCoordinator` will automatically:
     - Clear the gate.
     - Train candidate XGBoost models.
     - Validate schema 2.0.0 and directional metrics.
     - Atomically promote the trained model to `REAL_PRODUCTION_ACTIVE`.
