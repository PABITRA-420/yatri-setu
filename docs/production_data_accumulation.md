# Production Historical Data Accumulation & Readiness Pipeline

## 1. Overview & System Purpose

The **Yatri Setu Production Historical Data Accumulation Pipeline** is responsible for collecting, validating, time-aligning, and auditing genuine tourism observations across the six canonical destinations of the Eastern Himalayan region in West Bengal.

The pipeline adheres to the core engineering principle:
> **Never fabricate historical data or weaken the ProductionEligibilityGate simply to make XGBoost train.**

The dataset grows organically through daily automated captures and legitimate backfills from first-party ledgers, official gazette calendars, and regional event registries.

---

## 2. Canonical Destinations & Normalization

All accumulation pathways strictly enforce the six canonical destination identifiers:

| Canonical ID | Display Name | Category | Capacity Baseline | Primary Aliases & Normalization Rules |
| :--- | :--- | :--- | :--- | :--- |
| `darjeeling` | Darjeeling | Urban Hill Hub | 5,000 | `darj`, `darjeeling_town`, `darjeeling-district`, `queen of hills` |
| `kalimpong` | Kalimpong | Ridge Town Hub | 3,000 | `kalimpong_town`, `kalimpong-district`, `kalimpong_municipality` |
| `mirik` | Mirik | Lake Valley | 2,500 | `mirik_lake`, `mirik_bazar`, `mirik town` |
| `lava` | Lava | Forest Ecotourism | 1,000 | `lava_bazar`, `lava_village` |
| `lolegaon` | Lolegaon | Rural Ecotourism | 800 | `lolegaon_forest`, `loleygaon`, `kaffer`, `kaffer_village` |
| `rishop` | Rishop | High Ridge Hamlet | 600 | `rishop_village`, `rishyap`, `rishyap_village` |

Normalization is handled deterministically by `backend/app/services/historical/destination_registry.py`. Unrecognized destinations raise a strict `ValueError` and are rejected prior to persistence.

---

## 3. Data Source & Signal Audit

Every observation signal is tracked with signal-level provenance, distinguishing genuine real-world measurements from unavailable telemetry:

| Signal | Source System | Provider Mode | Cadence | Destination Coverage | Availability in REAL Mode | Missingness Handling | ML Training Eligibility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Confirmed Bookings** | PostgreSQL `bookings` ledger | `HISTORICAL` / `LIVE` | Continuous (Daily bucket) | All 6 | Genuine first-party count | NULL if 0 recorded | Eligible (Core) |
| **First-Party Search Demand** | PostgreSQL `demand_events` | `HISTORICAL` / `LIVE` | Continuous (Daily bucket) | All 6 | Genuine query telemetry | NULL if unqueried | Eligible (Core) |
| **Gazetted Holidays** | Holiday Calendar Engine | `HISTORICAL` / `COMPUTED` | Daily | All 6 | Official state gazette | Preserved score | Eligible (Core) |
| **Regional Events** | Regional Events Registry | `HISTORICAL` / `COMPUTED` | Daily | All 6 | Verified cultural catalog | 0 event pressure | Eligible (Core) |
| **Crowd Engine V2 Pressure** | Crowd Engine V2 Core | `COMPUTED` | Real-time | All 6 | Multi-signal current state | Ground truth target | Eligible (Core Target) |
| **Promenade Footfall** | Physical turnstile sensors | `UNAVAILABLE` | Daily | None historical | Unmeasured for past dates | Preserved as NULL | Excluded until live |
| **Hyper-local Weather** | Station sensor telemetry | `HISTORICAL` (live only) | Hourly | All 6 (live) | Unmeasured for past dates | Preserved as NULL | Excluded when NULL |
| **Corridor Traffic Delay** | Arterial delay telemetry | `HISTORICAL` (live only) | Real-time | All 6 (live) | Unmeasured for past dates | Preserved as NULL | Excluded when NULL |

---

## 4. Current Dataset Audit & Quality Profile

Audit of the PostgreSQL `historical_crowd_observations` table:

```text
REAL rows: 10
Distinct observation dates: 9
Temporal span: 18 days
Destinations represented: 6 / 6
Rows per destination:
  - darjeeling: 2
  - kalimpong:  3
  - mirik:       2
  - lava:        1
  - lolegaon:    1
  - rishop:      1
Quality Breakdown:
  - HIGH:    1 (10%)
  - MEDIUM:  0 (0%)
  - LOW:     5 (50%)
  - INVALID: 4 (40% - dates flagged with future buckets or missing target)
Core Signal Missingness: 68.4%
Core Signal Availability: 31.6%
```

### Accumulation Bottlenecks: Why 10 Rows and 18 Days?
The current dataset size reflects authentic historical data constraints:
1. **Zero Fabrication Policy**: Unlike synthetic benchmarking, genuine observations cannot be artificially multiplied. Each day represents a real calendar date.
2. **First-Party Ledger Span**: Confirmed bookings and verified search sessions only exist for dates when users actively engaged with the Yatri Setu platform.
3. **Absence of Historical Physical Telemetry**: Automated road sensors and local micro-climate stations were not historically deployed across remote hamlets like Rishop and Lolegaon prior to project inception.
4. **Idempotency Gate**: Re-running capture or backfill over existing dates updates records rather than duplicating them.

---

## 5. Architectural Safeguards

### A. Separation of Observation Date vs Ingestion Date
- **`observed_at`**: When the tourism state actually occurred.
- **`ingested_at`**: When Yatri Setu persisted the observation in the database.
- **`date_bucket`**: Canonical `YYYY-MM-DD` alignment string.

A backfilled record for September 1, 2026 captured on September 20, 2026 has:
$$\text{observed\_at} = \text{2026-09-01 12:00:00 UTC}$$
$$\text{ingested\_at} = \text{2026-09-20 23:28:00 UTC}$$

This separation eliminates temporal leakage in the XGBoost forecasting pipeline ($feature\_time < target\_time$).

### B. Idempotency & Duplicate Prevention
- Idempotency key: `{destination_id}_{date_bucket}_{dataset_mode}`.
- Repeated executions for the same destination and date bucket check existing signal values.
- Identical captures increment `duplicates_prevented` and avoid dirty database writes.
- Enforced by unique constraint `uq_dest_date_bucket_mode` on `(destination_id, date_bucket, dataset_mode)`.

### C. Partial Provider Failure Resilience
If an external provider (e.g. Weather API or Traffic corridor) fails or is offline during daily capture:
- The destination observation is **NOT discarded**.
- Available signals (bookings, search demand, holidays, events, capacity) are persisted.
- Unavailable signals remain strictly **`NULL`** with provenance `provider_mode: UNAVAILABLE`.
- Numeric values are **NEVER defaulted to zero**.

### D. Bounded Retries
The daily scheduler attempts up to `max_retries` (default 3) per destination with exponential backoff before logging an error in `failed_destinations`.

---

## 6. Readiness Diagnostics & Structural Projection

### A. Readiness Metrics
Exposed via `GET /api/admin/ml/production-readiness`:
- **Row Progress**: $\frac{REAL\_rows}{180}$ (e.g. $5.56\%$).
- **Temporal Progress**: $\frac{temporal\_span\_days}{30}$ (e.g. $60.0\%$).
- **Destination Coverage**: Distinct canonical destinations represented vs required ($\ge 3$ required, $\ge 20$ rows/destination).

### B. Structural Projection
Exposed via `readiness_metrics.projection`:
- Calculates the observed unique real row accumulation rate:
  $$Rate = \frac{REAL\_rows}{temporal\_span\_days}$$
- Estimates the completion date when structural thresholds ($rows \ge 180$, $days \ge 30$) would be met:
  $$Days = \max\left(\left\lceil \frac{180 - REAL\_rows}{Rate} \right\rceil, 30 - temporal\_span\_days\right)$$
- **Safety Rule**: If fewer than 2 distinct dates or 6 rows exist, returns:
  `{"available": false, "reason": "insufficient_accumulation_history"}`.
- **Safety Rule**: Structural projections are **purely diagnostic** and never guarantee XGBoost accuracy or influence model promotion.

---

## 7. Operational Endpoints

| Method | Path | Description | Backward Compatible |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/historical/coverage` | Detailed six-destination coverage report | Yes (Additive) |
| `GET` | `/api/historical/capture-status` | Operational scheduler capture health & timestamps | Yes (Additive) |
| `POST` | `/api/historical/daily-capture` | Scheduled daily observation capture | Yes |
| `GET` | `/api/admin/ml/production-readiness` | Complete ML production readiness & diagnostics | Yes |
| `POST` | `/api/admin/ml/retrain-if-eligible` | Atomic production retraining gate check | Yes |

---

## 8. Scheduler Integration

For automated external execution (Cron, Kubernetes CronJob, or Cloud Scheduler):
```bash
# Nightly capture at 23:55 UTC
curl -X POST "http://localhost:8000/api/historical/daily-capture?dataset_mode=REAL&max_retries=3"
```
The endpoint is completely idempotent and safe to run multiple times.
