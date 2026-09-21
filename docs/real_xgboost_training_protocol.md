# Real XGBoost Training Protocol & Leakage-Safe Promotion Specification

**Milestone**: Prompt 10 / Branch `v10`  
**System**: Yatri Setu Machine Learning Forecasting Pipeline  
**Document**: Leakage-Safe Feature Engineering, Chronological Splitting, Model Training, Validation, and Atomic Promotion Protocol  

---

## 1. Protocol Overview & Non-Negotiable Tenets

This protocol specifies the exact operational lifecycle executed when the immutable `ProductionEligibilityGate` certifies that genuine REAL historical tourism observations satisfy all production criteria.

### Core Principles:
1. **Zero Synthetic Contamination**: The production training dataset contains strictly $0$ synthetic rows and $0$ mixed rows. Synthetic benchmark models remain quarantined.
2. **Strict Chronological Ordering**: Random temporal shuffles are prohibited. Training dates strictly precede validation dates, which strictly precede held-out test dates.
3. **Strict Temporal Inequality**: For every forecasting instance $(x_t, y_{t+h})$, $t+h > t$. No future information, booking pace after $t$, or same-day targets leak into feature vectors.
4. **Native Missing-Value Handling**: Unmeasured physical signals (footfall turnstiles, road sensors) remain `NaN` / `NULL`. They are never imputed with arbitrary constants like 0 or 50.
5. **Baseline Superiority Required**: A candidate XGBoost model is only promoted if its chronological held-out MAE is equal to or lower than `baseline_rule_v2`.

---

## 2. End-to-End Training & Promotion Sequence

```text
1. DATASET ELIGIBILITY CERTIFICATION
   Verify ProductionEligibilityGate: REAL mode, >=180 rows, >=30 days, >=3 dests, >=20 rows/dest,
   100% target availability, core missingness <=70%, target variance >=4.0.
                        ↓
2. DATASET FINGERPRINTING & DUPLICATE PREVENTION
   Compute SHA-256 fingerprint of dataset snapshot. If identical to active model metadata,
   skip duplicate retraining.
                        ↓
3. CHRONOLOGICAL DATASET SPLIT
   Sort all ML-eligible rows by (date_bucket, destination_id) ascending.
   Split: 70% Train (earliest dates) | 15% Validation (middle dates) | 15% Test (latest dates).
                        ↓
4. MULTI-HORIZON FEATURE ENGINEERING (Schema 2.0.0)
   StandardFeatureBuilder extracts exactly 22 features (8 signal indicators, 7 calendar cycles,
   1 leading ratio, 6 one-hot destination archetypes).
                        ↓
5. CANDIDATE ARTIFACT TRAINING
   Train XGBoostRegressor into isolated candidate path (crowd_xgb_v1_candidate.joblib).
   Horizons supported: H ∈ {1, 3, 7, 14} days.
                        ↓
6. CANDIDATE ARTIFACT VALIDATION
   - Confirm candidate artifact reloads successfully from disk.
   - Confirm feature names count == 22 and exact schema order matches StandardFeatureBuilder.
   - Confirm model metadata contains dataset_mode == REAL and production_eligible == True.
                        ↓
7. HELD-OUT CHRONOLOGICAL EVALUATION
   Compute REAL PRODUCTION VALIDATION METRICS on the 15% held-out test split:
   Overall MAE, RMSE, R², Directional Accuracy, and per-horizon breakdowns (H=1, 3, 7, 14).
                        ↓
8. BASELINE COMPARISON & PROMOTION DECISION
   Evaluate candidate against baseline_rule_v2 on the identical test split.
   If candidate MAE <= baseline MAE and R² >= 0.0: PROCEED TO PROMOTE.
   If candidate MAE > baseline MAE or R² < -0.5: PROMOTION_REJECTED (Candidate discarded).
                        ↓
9. ATOMIC PROMOTION & ROLLBACK CAPABILITY
   - Create backup copy of active production artifact (crowd_xgb_v1_backup.joblib).
   - Atomically move candidate into production position (crowd_xgb_v1.joblib).
   - Reload model in ModelRegistry. If reload fails, immediately restore from backup.
   - Attach training provenance metadata.
```

---

## 3. Canonical 22-Dimensional Feature Schema (Version 2.0.0)

Both training and inference feature vectors must be built by `StandardFeatureBuilder` in this exact order:

| Index | Feature Name | Description | Source / Aggregation |
| :---: | :--- | :--- | :--- |
| 0 | `historical_footfall` | Physical pedestrian volume (NULL if unmeasured) | Turnstile sensors / `np.nan` |
| 1 | `accommodation_occupancy` | Percentage of published homestay rooms booked | First-party ledger / capacity |
| 2 | `booking_demand` | Confirmed forward booking creation volume | PostgreSQL `bookings` ledger |
| 3 | `search_demand` | Search and discovery query intensity | PostgreSQL `demand_events` |
| 4 | `event_pressure` | Active cultural and tourism event impact score | District Tourism Registry |
| 5 | `holiday_pressure` | Official state/national gazetted holiday score | Official Gazette Calendar |
| 6 | `weather_pressure` | Inverse comfort index (NULL if unmeasured) | Station telemetry / `np.nan` |
| 7 | `traffic_pressure` | Arterial transit delay pressure (NULL if unmeasured) | Corridor telemetry / `np.nan` |
| 8 | `day_of_week` | Integer day index (0 = Monday, 6 = Sunday) | Target calendar date |
| 9 | `is_weekend` | Boolean weekend flag (Friday, Saturday, Sunday) | Target calendar date |
| 10 | `month` | Target calendar month index (1 to 12) | Target calendar date |
| 11 | `day_of_year` | Day of year index (1 to 366) | Target calendar date |
| 12 | `search_to_booking_ratio` | Leading intent ratio: $\text{search} / (\text{booking} + 10^{-3})$ | Telemetry quotient |
| 13 | `is_peak_summer` | Summer peak tourism flag (April, May, June) | Calendar month |
| 14 | `is_peak_autumn` | Autumn festive season flag (Sept, Oct, Nov) | Calendar month |
| 15 | `target_horizon_days` | Forecast horizon ($H = 1, 3, 7, 14$) | Prediction target horizon |
| 16 | `dest_darjeeling` | One-hot destination indicator | Canonical destination ID |
| 17 | `dest_kalimpong` | One-hot destination indicator | Canonical destination ID |
| 18 | `dest_mirik` | One-hot destination indicator | Canonical destination ID |
| 19 | `dest_lava` | One-hot destination indicator | Canonical destination ID |
| 20 | `dest_lolegaon` | One-hot destination indicator | Canonical destination ID |
| 21 | `dest_rishop` | One-hot destination indicator | Canonical destination ID |

---

## 4. Real vs Synthetic Model Isolation Matrix

| Attribute | REAL Production Model | SYNTHETIC Benchmark Model |
| :--- | :--- | :--- |
| **Dataset Mode** | `REAL` | `SYNTHETIC` |
| **Data Sources** | First-party PostgreSQL ledgers, gazette, events | Seeded synthetic generator (`crowd_observations.csv`) |
| **Production Gate** | Must pass 100% of ProductionEligibilityGate | Bypassed for development & CI benchmarks |
| **Production Eligibility** | `production_eligible = True` | `production_eligible = False` |
| **Authoritative Usage** | Serves live traveler predictions when promoted | Strictly offline benchmarking & demonstration |
| **Reported Metrics** | Chronological held-out real observations | Test split on synthetic benchmark |
