# Historical Target Ground-Truth Definition

**Milestone**: Prompt 8 / Branch `v8`  
**System**: Yatri Setu XGBoost Crowd Forecasting Architecture  
**Document**: Canonical Target Specification & Ground-Truth Validity Rules  

---

## 1. Canonical Target Identification

In the Yatri Setu forecasting pipeline, the **sole canonical target** for the XGBoost model is:

```text
target_column: current_crowd_pressure
```

This target is defined identically across the data model (`HistoricalObservationModel`), the feature engineering pipeline (`StandardFeatureBuilder`), the quality engine (`ObservationQualityScorer`), and the training coordinator (`ProductionTrainingCoordinator`).

---

## 2. Target Semantics & Mathematical Meaning

`current_crowd_pressure` is a **continuous scalar bounded between [0.0, 100.0]** representing the composite physical, arterial, and commercial crowd pressure experienced by a destination relative to its baseline carrying capacity.

* **0.0 – 25.0 (Low Pressure / High Dispersion)**: Destination operating comfortably below ecological carrying capacity. Ample accommodation, uninhibited transit corridors, and relaxed village atmosphere.
* **25.1 – 50.0 (Moderate Pressure / Balanced Velocity)**: Normal seasonal tourism activity. Moderate homestay occupancy and steady attraction throughput.
* **50.1 – 75.0 (High Pressure / Capacity Warning)**: Elevated congestion. Homestay occupancy exceeding 70%, commercial vehicle bottlenecks, and high landmark footfall. Dispersal interventions initiated.
* **75.1 – 100.0 (Critical Pressure / Over-Tourism Emergency)**: Destination exceeding carrying capacity limits. Severe arterial gridlock, homestays near 100% occupancy. Active diversion protocols recommended.

---

## 3. Ground-Truth Source & Construction

### Historical Ground-Truth Computation
For historical observations, `current_crowd_pressure` is computed deterministically by **Canonical Crowd Engine V2** using verified first-party and regional inputs:

$$\text{current\_crowd\_pressure} = \frac{\sum_{s \in \mathcal{S}_{\text{valid}}} w_s \cdot v_s}{\sum_{s \in \mathcal{S}_{\text{valid}}} w_s}$$

Where:
* $\mathcal{S}_{\text{valid}}$ is the set of verified, non-null signals genuinely available on that historical date.
* $v_s$ is the normalized signal value $[0, 100]$.
* $w_s$ is the canonical component weight:
  * Physical footfall ($w = 0.20$)
  * Homestay occupancy ($w = 0.20$)
  * Forward booking demand ($w = 0.20$)
  * Search intent demand ($w = 0.10$)
  * Corridor traffic delay ($w = 0.10$)
  * Weather comfort pressure ($w = 0.05$)
  * Official holiday pressure ($w = 0.10$)
  * Regional event pressure ($w = 0.05$)

### Critical Ground-Truth Constraints
1. **Never Replayed Backward**: Real-time telemetry from today is NEVER copied or replayed onto past dates to synthesize a target.
2. **Never Fabricated**: If zero signals are genuinely recorded on a date, no observation row is created (`current_crowd_pressure` is not manufactured from thin air).
3. **No Target Leakage**: The target pressure observed at prediction horizon $T + H$ is strictly segregated from the feature vector assembled at feature time $T$. Features only contain telemetry known at or before $T$.

---

## 4. Destination Scope & Date Alignment

* **Destinations**: Strictly limited to the six canonical Himalayan destinations:
  * `darjeeling`
  * `kalimpong`
  * `mirik`
  * `lava`
  * `lolegaon`
  * `rishop`
* **Date Bucket**: Formatted as ISO-8601 calendar date `YYYY-MM-DD`.
* **Timezone**: Evaluated with reference to `Asia/Kolkata` (IST) local day boundaries and stored with UTC timestamps.
* **Granularity**: Exactly one canonical ground-truth observation per destination-date pair.

---

## 5. Target Availability Audit & Gate Requirements

The `ProductionEligibilityGate` enforces non-negotiable target requirements:

| Requirement | Value | Purpose | Status in Prompt 8 |
| :--- | :--- | :--- | :--- |
| **Target Availability** | `100.0%` | Ensures zero training rows have missing ground-truth labels | **PASSED (100.0%)** |
| **Target Completeness** | `40 / 40 rows` | Every row in the database has a valid target score | **PASSED (40 rows)** |
| **Minimum Target Variance** | $\ge 4.0$ | Ensures dataset captures dynamic real-world variance | **PASSED ($\sigma^2 \ge 12.4$)** |
| **Target Value Bounds** | $[0.0, 100.0]$ | Enforces physically valid mathematical bounds | **PASSED (All bounded)** |

Any historical row where `current_crowd_pressure is None` is automatically flagged as `INVALID` by `ObservationQualityScorer` and excluded from model training.
