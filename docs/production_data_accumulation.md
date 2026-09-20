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
| `lava` | Lava | Forest Ecotourism | 1,500 | `lava_bazar`, `lava_village` |
| `lolegaon` | Lolegaon | Rural Ecotourism | 1,200 | `lolegaon_forest`, `loleygaon`, `kaffer`, `kaffer_village` |
| `rishop` | Rishop | High Ridge Hamlet | 1,000 | `rishop_village`, `rishyap`, `rishyap_village` |

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

## 4. Current Dataset Audit & Quality Profile (Updated Prompt 9 / v9)

Audit of the PostgreSQL `historical_crowd_observations` table:

```text
Total REAL rows in database: 88
ML-Eligible REAL rows: 60 (Expanded across all 6 destinations for 10 distinct dates)
INVALID audit records: 28 (Retained in database for audit integrity; excluded from ML)
Distinct observation dates: 10
Earliest genuine date: 2026-08-15
Latest genuine date: 2026-09-20
Temporal span: 37 days (Meets the >= 30 days requirement!)
Destinations represented: 6 / 6 (100% coverage)
Rows per destination:
  - darjeeling: 10
  - kalimpong:  10
  - mirik:       10
  - lava:        10
  - lolegaon:    10
  - rishop:      10
Quality Breakdown:
  - HIGH:    60 (100% of ML-eligible observations)
  - MEDIUM:  0 (0%)
  - LOW:     0 (0%)
  - INVALID: 28 (Retained for audit trail; excluded from ML gate)
Target Availability: 100.0% (60 / 60)
Core Missingness: 30.0% (Well within the <= 70% threshold)
Target Variance: 204.61 (Well above the >= 4.0 threshold)
Synthetic rows in REAL: 0 (Strictly isolated)
```

---

## 5. Production Eligibility Evaluation & Structural Accumulation Projection

Evaluating the dataset against `ProductionEligibilityGate`:

| Gate Requirement | Threshold | Current Value | Status |
| :--- | :---: | :---: | :---: |
| **Dataset Mode** | `REAL` | `REAL` | **PASS** |
| **Minimum Real Rows** | $\ge 180$ | `60` | **FAIL (Needs 120 rows)** |
| **Temporal Span** | $\ge 30\text{ days}$ | `37 days` | **PASS** |
| **Minimum Destinations** | $\ge 3$ | `6` | **PASS** |
| **Minimum Rows per Destination** | $\ge 20$ | `10` | **FAIL (Needs 10 rows/dest)** |
| **Target Availability** | $100.0\%$ | `100.0%` | **PASS** |
| **Maximum Core Missingness** | $\le 70.0\%$ | `30.0%` | **PASS** |
| **Minimum Target Variance** | $\ge 4.0$ | `204.61` | **PASS** |

### Structural Accumulation Projection
* **Label**: `STRUCTURAL ACCUMULATION PROJECTION` (Explicitly not prediction accuracy or model skill)
* **Observed Row Accumulation Rate**: 1.62 rows/day
* **Rows Needed**: 120 rows
* **Estimated Days to Gate Ready**: ~74 days
* **Estimated Gate Ready Date**: December 3, 2026 (assuming standard daily capture cadence across all 6 destinations)

---

## 6. Daily Capture & Idempotency Safeguards

* Daily scheduled ingestion via `POST /api/historical/daily-capture` records 6 genuine observations per day.
* Unique constraint `uq_dest_date_bucket_mode` prevents duplicate rows for the same destination and date.
* Missing physical signals (footfall, weather, traffic) remain `NULL` with `UNAVAILABLE` provenance.
