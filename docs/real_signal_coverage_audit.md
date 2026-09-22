# Yatri Setu — Real Signal Coverage & ML Feasibility Audit (Prompt 6)

> **Mandatory Policy Statement:**  
> **XGBoost production readiness depends on genuine historical data satisfying the existing eligibility gate. Synthetic benchmark performance does not establish real-world forecasting accuracy.**

---

## 1. Executive Summary

This audit evaluates the real-world availability, source lineage, provider mode, and missingness characteristics of all **22 features** defined in the XGBoost Schema 2.0.0 (`StandardFeatureBuilder`).

The features are partitioned into:
- **Direct Telemetry Signals** (8 features): Physical sensors, booking ledgers, user demand events, calendar schedules, weather/traffic conditions.
- **Derived / Interaction Features** (8 features): Temporal cycle indexes, peak season indicators, leading search-to-booking ratio, forecast horizon conditioning.
- **Destination Categorical Archetypes** (6 features): One-hot destination flags for the 6 canonical circuits.

---

## 2. 22-Feature Coverage & Feasibility Audit Matrix

| Feature | Source | Provider Mode | Historical Available | Live Available | Missingness (%) | Backfillable | ML Eligible | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `historical_footfall` | Promenade / Gate Sensors | `UNAVAILABLE` | No | Live Only (simulated/offline) | 100.0% | No | Conditional | Unmeasured historically. Must remain `NULL` (never fabricated). |
| `accommodation_occupancy` | Homestay Reservation Ledger | `HISTORICAL` / `UNAVAILABLE` | Yes (where inventory active) | Yes | 60.0% | Yes | Yes | Derived from confirmed bookings & published homestay capacities. |
| `booking_demand` | PostgreSQL `bookings` Ledger | `HISTORICAL` | Yes (311 verified records) | Yes | 40.0% | Yes | Yes | High-quality first-party confirmed stays across Kalimpong and Rishop. |
| `search_demand` | PostgreSQL `demand_events` Ledger | `HISTORICAL` | Yes (807 verified events) | Yes | 60.0% | Yes | Yes | Genuine user searches, destination views, availability requests. |
| `event_pressure` | Regional Cultural & Tourism Registry | `HISTORICAL` | Yes | Yes | 0.0% | Yes | Yes | Curated verified festival dates (Tea festivals, Losar, cultural fairs). |
| `holiday_pressure` | Official West Bengal Gazette | `HISTORICAL` | Yes | Yes | 0.0% | Yes | Yes | Official government gazetted holidays and long-weekend surge indexes. |
| `weather_pressure` | IMD / Open-Meteo Telemetry | `LIVE` / `UNAVAILABLE` | Live only (historical db table unpopulated) | Yes | 90.0% | Live accumulation | Conditional | Station readings available in real time; historical tables lack historical telemetry. |
| `traffic_pressure` | TomTom Arterial Corridor Telemetry | `LIVE` / `UNAVAILABLE` | Live only (historical db table unpopulated) | Yes | 80.0% | Live accumulation | Conditional | Corridor bottlenecks tracked live; historical telemetry is unmeasured. |
| `day_of_week` | Observation Timestamp | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | Deterministic weekday index (0=Monday to 6=Sunday). |
| `is_weekend` | Observation Timestamp | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | Deterministic binary flag (Friday, Saturday, Sunday). |
| `month` | Observation Timestamp | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | Deterministic calendar month (1 to 12). |
| `day_of_year` | Observation Timestamp | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | Annual seasonality index (1 to 365/366). |
| `search_to_booking_ratio` | Search & Booking Ledgers | `COMPUTED` / `UNAVAILABLE` | Yes (where both exist) | Yes | 60.0% | Yes | Yes | Leading indicator; evaluates conversion pressure $\frac{\text{search}}{\text{booking} + 0.001}$. |
| `is_peak_summer` | Calendar Month | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | Active during April, May, June peak tourism window. |
| `is_peak_autumn` | Calendar Month | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | Active during September, October, November Durga Puja / post-monsoon. |
| `target_horizon_days` | Horizon Parameter | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | Conditioning parameter $H \in \{1, 3, 7, 14\}$ days ahead. |
| `dest_darjeeling` | Destination Registry | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | One-hot destination indicator. |
| `dest_kalimpong` | Destination Registry | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | One-hot destination indicator. |
| `dest_mirik` | Destination Registry | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | One-hot destination indicator. |
| `dest_lava` | Destination Registry | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | One-hot destination indicator. |
| `dest_lolegaon` | Destination Registry | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | One-hot destination indicator. |
| `dest_rishop` | Destination Registry | `COMPUTED` | Yes | Yes | 0.0% | Yes | Yes | One-hot destination indicator. |

---

## 3. Findings & Strategy for Genuine Telemetry Enrichment

1. **High-Integrity Core Signals**:
   - Calendar, holiday, regional event, temporal cycles, and destination indicators have **0% missingness** and 100% historical verifiability.
   - First-party booking and demand event ledgers have **high signal-to-noise ratio** with 311 confirmed bookings and 807 demand events.
2. **Missing Sensor Telemetry**:
   - Physical footfall, historic arterial traffic delays, and historic weather lack historical databases in the project repository.
   - In accordance with the hard no-fabrication rule, these signals are explicitly preserved as `NULL` (`np.nan` for XGBoost native split handling) with `provider_mode = "UNAVAILABLE"`.
3. **Path to Organic Production Eligibility**:
   - By capturing 6 genuine observations daily via `POST /api/historical/daily-capture`, live weather, live traffic, and live Crowd Engine V2 scores are continuously persisted.
   - The dataset organically marches toward the $\ge 180$ row / $\ge 30$ day threshold required by the `ProductionEligibilityGate`.
