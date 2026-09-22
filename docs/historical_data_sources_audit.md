# Yatri Setu — Historical Tourism Data Sources & Provenance Audit

> **Mandatory Policy Statement:**  
> **XGBoost production readiness depends on genuine historical data satisfying the existing eligibility gate. Synthetic benchmark performance does not establish real-world forecasting accuracy.**

---

## 1. Executive Summary

Yatri Setu utilizes a dual-engine architecture:
- **Crowd Engine V2**: Canonical source of truth for **CURRENT** crowd pressure and immediate dispersal recommendations across the 6 Eastern Himalayan destinations.
- **XGBoost Multi-Horizon Forecasting Engine**: Forecaster for **FUTURE** crowd dynamics across horizons $H \in \{1, 3, 7, 14\}$ days.

To transition XGBoost from `BaselineRuleModel` fallback to production forecasting, training data must consist of genuine historical observations that satisfy the rigorous `ProductionEligibilityGate`. **Fabrication, silent interpolation, backward projection of live data, or relabeling synthetic data as REAL is strictly prohibited.**

This document provides a formal audit of all data sources currently available to Yatri Setu, their classification, provenance rules, backfill capabilities, and path toward production eligibility.

---

## 2. Real Data Source Audit & Classification Matrix

Each data source is classified into exactly one of:
`REAL` | `LIVE` | `CACHED` | `HISTORICAL` | `COMPUTED` | `SYNTHETIC` | `DEMO` | `MOCK` | `UNAVAILABLE`

| Source Name | Signal Provided | Historical Availability | Time Resolution | Geographic Coverage | Timestamp Semantics | Reliability | Usable Legally? | Can Enter REAL Data? | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **PostgreSQL Booking Ledger** (`bookings`) | Confirmed tourist arrivals, guest counts, room nights | 311+ verified ledger records (Oct–Dec 2026) | Daily bucket (`check_in_date`) | Kalimpong, Rishop | Transaction commit & check-in date | High (100% first-party DB) | Yes (First-party) | **Yes** | `HISTORICAL` |
| **PostgreSQL Demand Ledger** (`demand_events`) | User search intent, destination views, booking requests | 807+ verified interactions | Event timestamp (`created_at`) | All 6 canonical destinations | Exact event UTC timestamp | High (100% first-party telemetry) | Yes (First-party) | **Yes** | `HISTORICAL` |
| **West Bengal Gazetted Calendar** (`holiday_engine`) | State gazetted holidays, long-weekend flags, festival names | Deterministic calendar rules for current/past/future years | Daily bucket | West Bengal / Kalimpong / Darjeeling | Calendar date | Very High (Official State Gazette) | Yes (Public record) | **Yes** | `HISTORICAL` |
| **Eastern Himalayan Cultural Catalog** (`events_engine`) | Regional festivals, cultural gatherings, tea festivals | Curated calendar of verified annual dates | Daily bucket | Darjeeling, Kalimpong, Kurseong, Mirik | Event occurrence date | High (Curated public calendar) | Yes (Public domain) | **Yes** | `HISTORICAL` |
| **Destination Capacity Registry** (`DestinationModel`) | Physical carrying capacities, baseline visitor thresholds | Static baseline metadata | Perpetual | 6 canonical destinations | Registration date | High (Verified local capacity) | Yes (First-party) | **Yes** | `COMPUTED` |
| **Promenade Footfall Sensors / Counters** | Physical footfall volume, gate counter tallies | None currently recorded in DB | Daily | None (Simulated or Null) | Sensor timestamp | N/A (Not deployed) | N/A | **No** (Must remain `NULL`) | `UNAVAILABLE` |
| **Physical Traffic Corridors / ANPR** | NH-10 / Hill Cart Road vehicular volume | None persisted historically | Daily | Corridor bottlenecks | Camera timestamp | N/A (Not deployed) | N/A | **No** (Must remain `NULL`) | `UNAVAILABLE` |
| **Station Microclimate Weather Telemetry** | Precipitation, temperature, visibility, storm warnings | Live telemetry only; no historical DB telemetry | Hourly / Daily | Darjeeling Ridge, Kalimpong Hill | Telemetry recording timestamp | Moderate (Live API only) | Open-Meteo / IMD | **No** (Live != Historical) | `UNAVAILABLE` |
| **Deterministic Synthetic Engine** (`synthetic_dataset.py`) | Multi-seasonal synthetic tourism benchmarks | Programmatic generator (365 days) | Daily | All 6 canonical destinations | Generated benchmark date | High (Math model) | Yes (Testing/CI only) | **No** (Benchmark Only) | `SYNTHETIC` |

---

## 3. Deep Dive on Legitimate First-Party Sources

### 3.1. PostgreSQL Booking Ledger (`BookingModel`)
- **Signal**: `booking_demand` (normalized 0–100 scale relative to destination carrying capacity).
- **Semantics**: Represents genuine confirmed hotel/homestay reservations logged by travelers.
- **Aggregation**: Total guest nights for destination $d$ on date $t$:
  $$\text{booking\_demand} = \min\left(100.0, \frac{\sum \text{confirmed guests for } d \text{ on } t}{\text{Destination Carrying Capacity}} \times 100\right)$$
- **Provenance**: `source_type = "POSTGRES_LEDGER"`, `source_name = "booking_ledger"`.
- **Eligibility**: Genuine, audit-traceable, zero fabrication.

### 3.2. PostgreSQL Demand Ledger (`DemandEventModel`)
- **Signal**: `search_demand` (normalized 0–100 scale relative to peak volume).
- **Semantics**: Aggregates distinct user search and view events targeting destination $d$ on date $t$.
- **Aggregation**:
  $$\text{search\_demand} = \min\left(100.0, \frac{\text{distinct search queries}}{\text{scaling factor (50)}} \times 100\right)$$
- **Provenance**: `source_type = "POSTGRES_LEDGER"`, `source_name = "demand_events_ledger"`.
- **Eligibility**: Genuine first-party user intent.

### 3.3. West Bengal Gazetted Holiday Engine (`holiday_engine`)
- **Signal**: `holiday_pressure`, `is_holiday`, `is_weekend`, `holiday_name`.
- **Semantics**: Gazetted public holidays and regional festivals officially observed in West Bengal (e.g., Durga Puja, Diwali, Republic Day, Losar).
- **Provenance**: `source_type = "GOVERNMENT_GAZETTE"`, `source_name = "wb_gazetted_calendar"`.
- **Eligibility**: Official calendar data, perfectly verifiable for any historical date.

### 3.4. Regional Cultural Events Catalog (`events_engine`)
- **Signal**: `event_pressure`, `active_events_count`.
- **Semantics**: Verified regional events and fairs occurring in Darjeeling and Kalimpong districts.
- **Provenance**: `source_type = "CULTURAL_CALENDAR"`, `source_name = "eastern_himalayan_events"`.
- **Eligibility**: Legitimate factual calendar data.

### 3.5. Unmeasured Signals (Footfall, Weather, Corridor Traffic)
- **Signal**: `footfall`, `traffic_pressure`, `weather_pressure`.
- **Policy**: When physical sensors or historical telemetry databases are not actively populated for a historical date, the system **NEVER** fabricates or guesses values.
- **Value**: `NULL` (`None`).
- **Provenance**: `"UNAVAILABLE"`, `source_name = "unmeasured_signal"`, notes: `"No physical sensor recording available for historical date"`.

---

## 4. Destination Mapping & Canonical Authority

The canonical destinations are strictly bounded to the 6 destinations authorized in Yatri Setu:
1. `darjeeling` (Carrying Capacity: 5,000)
2. `kalimpong` (Carrying Capacity: 3,000)
3. `mirik` (Carrying Capacity: 2,000)
4. `lava` (Carrying Capacity: 800)
5. `lolegaon` (Carrying Capacity: 600)
6. `rishop` (Carrying Capacity: 500)

### Mapping Rules:
- Geographic units must match canonical destination IDs exactly (case-insensitive, whitespace-trimmed).
- Sub-localities (e.g., Tiger Hill, Batasia Loop, Mall Road) map exclusively to `darjeeling`.
- Deolo Hill, Durpin Dara map exclusively to `kalimpong`.
- Unknown or ambiguous locations are **REJECTED** and never guessed.

---

## 5. Provenance Model

Every historical record stored in `historical_crowd_observations` contains:
- `id`: Deterministic hash `{destination_id}_{date_bucket}_{dataset_mode.lower()}` enforcing idempotency.
- `destination_id`: Authoritative destination identifier.
- `date_bucket`: `YYYY-MM-DD` in Asia/Kolkata (IST) / UTC aligned.
- `observed_at`: Ingestion timestamp.
- `dataset_mode`: `REAL`, `SYNTHETIC`, or `MIXED`.
- `signal_provenance`: JSON dictionary providing signal-level lineage:
  ```json
  {
    "booking_demand": {
      "provenance": "HISTORICAL",
      "source_type": "POSTGRES_LEDGER",
      "source_name": "booking_ledger",
      "source_timestamp": "2026-10-15T00:00:00Z",
      "ingestion_timestamp": "2026-09-20T18:40:00Z",
      "notes": "Verified confirmed bookings: 12 guests"
    },
    "footfall": {
      "provenance": "UNAVAILABLE",
      "source_type": "SENSOR_TELEMETRY",
      "source_name": "unmeasured_signal",
      "notes": "No physical sensor recording available for historical date"
    }
  }
  ```

---

## 6. XGBoost Leakage Safety Rules

To prevent temporal leakage in multi-horizon forecasting ($H \in \{1, 3, 7, 14\}$):
1. **Strict Horizon Inequality**: For every observation pair:
   $$\text{feature\_date} < \text{target\_date}$$
   $$\text{target\_date} - \text{feature\_date} = H \text{ days}$$
2. **Target Isolation**: Target crowd pressure is strictly computed at $\text{target\_date}$ and NEVER included in the feature vector at $\text{feature\_date}$.
3. **No Future Signals**: Signals at $\text{feature\_date}$ rely solely on information knowable at or before that date. Future weather, bookings made after the date, or future searches are excluded.

---

## 7. Production Eligibility Gate (`ProductionEligibilityGate`)

Under Prompt 4 & Prompt 5, the production eligibility gate remains unmodified and strictly enforced:
- `dataset_mode == "REAL"`
- Total rows $\ge 180$
- Unique destinations $\ge 3$
- Rows per destination $\ge 20$
- Temporal span $\ge 30$ days
- Target availability $= 100\%$
- Missingness of core signals $\le 70\%$
- Target variance $\ge 4.0$

### Outcome Evaluation:
- If all criteria pass: Model status becomes `PRODUCTION_ELIGIBLE`, permitting XGBoost production registration.
- If any criterion fails: Status is `INSUFFICIENT_DATA` (or specific failure reason). The system continues using `BaselineRuleModel` (Crowd Engine V2 telemetry + domain rules).

---

## 8. Continuous Accumulation of Future Real Observations

To naturally achieve production eligibility over time without data fabrication:
1. **Daily Scheduled Capture**:
   - Endpoint: `POST /api/historical/daily-capture`
   - Gathers live telemetry from Crowd Engine V2, active bookings, demand events, and holiday calendar daily.
   - Retries up to 3 times per destination on transient failure.
   - Persists idempotently into `historical_crowd_observations` with `dataset_mode="REAL"`.
2. **Organic Growth**:
   - Each passing day adds 6 genuine observations (1 per canonical destination).
   - In 30 days, 180 genuine observations accumulate across all 6 destinations, organically crossing the 180-row / 30-day temporal threshold.
