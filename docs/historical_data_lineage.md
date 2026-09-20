# Historical Data Lineage & Provenance Specification

**Milestone**: Prompt 9 / Branch `v9`  
**System**: Yatri Setu Historical Tourism Data Foundation  
**Auditor**: End-to-End Signal Provenance, Aggregation & Isolation Audit  

---

## 1. End-to-End Data Lineage Architecture

The flow of historical telemetry from raw event to machine learning training is governed by strict deterministic transformations:

```text
RAW FIRST-PARTY SOURCES
(PostgreSQL Bookings, Demand Events, Homestay Inventory, Gazette, Event Catalog)
                                ↓
                 CANONICAL DESTINATION NORMALIZATION
 (Maps aliases/suffixes to darjeeling, kalimpong, mirik, lava, lolegaon, rishop)
                                ↓
                  LOCAL TIMEZONE & DATE BUCKETING
 (IST day boundaries [00:00:00 - 23:59:59] mapped to canonical YYYY-MM-DD bucket)
                                ↓
               DETERMINISTIC SIGNAL AGGREGATION
      (Forward creation velocity separated from active guest stays)
                                ↓
                  TARGET GROUND-TRUTH RESOLUTION
       (Canonical Crowd Engine V2 normalized over verified signals)
                                ↓
                 SIGNAL-LEVEL PROVENANCE ATTACHMENT
   (source, provider_mode, confidence, raw_value, raw_unit, contextual notes)
                                ↓
                DETERMINISTIC QUALITY EVALUATION
                 (Grades: HIGH, MEDIUM, LOW, INVALID)
                                ↓
                  REAL HISTORICAL DATASET STORAGE
           (Table: historical_crowd_observations in PostgreSQL)
                                ↓
                  PRODUCTION ELIGIBILITY GATE
 (Enforces 180 rows, 30 days span, 3 dests, 20 rows/dest, 100% target availability)
                                ↓
            CHRONOLOGICAL MULTI-HORIZON ML TRAINING
                     (XGBoost Candidate Artifact)
                                ↓
               ATOMIC PROMOTION OR BASELINE RETENTION
```

---

## 2. Granular Signal Lineage Matrix

| Signal Name | Primary Source Table / Provider | Raw Event / Field | Aggregation Logic | Provider Mode | Unit | Provenance Confidence | Limitations & Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`booking_demand`** | `bookings` (PostgreSQL) | `created_at` timestamp | Count of confirmed booking reservations transacted on that date | `HISTORICAL` | `confirmed_created_bookings` | `0.98` | Measures forward reservation pace on platform; not total footfall |
| **`accommodation_occupancy`** | `bookings` & `homestays` (PostgreSQL) | `check_in_date`, `check_out_date`, `rooms_booked` | Active occupied rooms divided by total published capacity | `HISTORICAL` | `percent_occupancy` | `0.95` | Limited to verified published properties registered on Yatri Setu |
| **`search_demand`** | `demand_events` (PostgreSQL) | `timestamp`, `event_type` (`search`, `destination_selection`) | Count of user queries/views targeting destination on date | `HISTORICAL` | `search_queries` | `0.95` | Reflects digital traveler intent; never converted directly to tourist footfall |
| **`holiday_pressure`** | `holidays` (PostgreSQL) & District Calendar | Official gazetted holiday dates | Continuous scaling based on national/state status and weekend proximity | `HISTORICAL` | `holiday_scale_0_100` | `0.99` | Deterministic calendar rules; no subjective interpretation |
| **`event_pressure`** | `events` (PostgreSQL) & Tourism Registry | Catalogued festivals & fairs | Scaled active regional event count | `HISTORICAL` | `active_events_count` | `0.92` | District administration catalogued events only |
| **`weather_pressure`** | Meteorological telemetry | Station observations | Inverse comfort index calculated from temperature and precipitation | `HISTORICAL` or `UNAVAILABLE` | `celsius` | `0.90` | If genuine station records do not exist, strictly `NULL` |
| **`traffic_pressure`** | Arterial corridor sensors | Delay minutes on hill corridors | Congestion delay scaled to pressure | `HISTORICAL` or `UNAVAILABLE` | `delay_minutes` | `0.90` | If corridor sensors unavailable, strictly `NULL` |
| **`footfall`** | Promenade & entry gate sensors | Physical pedestrian count | Scaled physical promenade throughput | `HISTORICAL` or `UNAVAILABLE` | `pedestrians_per_hour` | `0.95` | Strictly `NULL` when sensor hardware not deployed. Never estimated from bookings |
| **`current_crowd_pressure`** (Target) | Canonical Crowd Engine V2 | Weighted composite of verified signals | Deterministic weighted rule over non-null inputs | `COMPUTED` | `composite_pressure_0_100`| `0.92` | Canonical target. Never manufactured without underlying verified signals |

---

## 3. Strict Provider Mode Classifications

Every historical observation enforces strict provenance tagging for each individual signal:

* **`REAL` / `HISTORICAL`**: Directly recorded first-party database events or measured historical sensor logs.
* **`LIVE`**: Live real-time incoming operational telemetry.
* **`CACHED`**: Recently retrieved live telemetry stored with short TTL.
* **`COMPUTED`**: Deterministically calculated by canonical algorithmic rules (e.g. Crowd Engine V2) from verified historical inputs.
* **`UNAVAILABLE`**: Truly unmeasured telemetry (e.g. absent hardware sensors). Signal value is strictly `None` / `NULL`.
* **`SYNTHETIC`**: Seeded benchmark data for deterministic testing. **Strictly quarantined from production training.**
* **`MOCK`**: Local development fallback for offline development.

---

## 4. Signal Isolation & Integrity Guarantees

1. **Zero Synthetic Leakage**:
   The `REAL` dataset mode in `historical_crowd_observations` contains strictly zero rows generated from synthetic noise or random seeds.
2. **Zero Guessing or Mean-Filling**:
   Unmeasured signals remain strictly `NULL`. The ML pipeline is built to handle sparse tabular matrices with native XGBoost missing-value handling.
3. **No Target Leakage into Features**:
   Features engineered for prediction horizon $T + H$ use only data available at $T$. Post-event telemetry is never used to construct pre-event features.
4. **Idempotency**:
   Rebuilding or re-ingesting observations for an existing destination and date bucket updates existing records in-place without creating duplicate rows.
5. **Separation of Physical Audit Records from ML-Eligible Rows**:
   Future test records (28 rows) are retained in the database for audit integrity but graded `INVALID` and excluded from ML feature construction and gate evaluation.
