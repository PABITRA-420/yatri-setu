# Yatri Setu — Accumulation Gap Analysis

## Overview

Prompt 11 establishes a deterministic **Accumulation Gap Detector** to classify every canonical destination and date observation across the historical accumulation horizon.

---

## 1. Classification Categories

Every date/destination tuple $(d, \text{dest})$ is strictly assigned one of the following states:

1. `CAPTURED_VALID`: Present in database, `dataset_mode == "REAL"`, valid canonical destination, non-null target, quality status `VALID`, passing ML criteria.
2. `CAPTURED_INVALID`: Present in database but flagged `INVALID` (e.g. 28 future/test records quarantined with zero ML eligibility).
3. `INCOMPLETE`: Present in database but lacking required telemetry or target.
4. `DUPLICATE`: Redundant duplicate records for the same destination and date bucket.
5. `MISSING`: Calendar date in the observed historical window with no observation record recorded.
6. `EXPECTED`: Total possible date/destination combinations ($6 \times \text{calendar days}$).

---

## 2. Current Measured Audit

From the authoritative database audit (evaluating the historical temporal window from `2026-06-15` to `2026-09-25`, encompassing 103 calendar days):

- **Expected Slots**: `618` (103 days $\times$ 6 canonical destinations)
- **CAPTURED_VALID**: `66` ML-eligible observations
- **CAPTURED_INVALID**: `28` isolated audit records
- **INCOMPLETE**: `0`
- **DUPLICATE**: `0`
- **MISSING**: `524` uncaptured historical destination-date slots

---

## 3. Destination Coverage Matrix

| Destination | Valid Rows | Target Completeness | Core Missingness | First Date | Latest Date |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `darjeeling` | 11 / 20 | 100.0% | 29.1% | 2026-06-15 | 2026-07-22 |
| `kalimpong` | 11 / 20 | 100.0% | 29.1% | 2026-06-15 | 2026-07-22 |
| `mirik` | 11 / 20 | 100.0% | 29.1% | 2026-06-15 | 2026-07-22 |
| `lava` | 11 / 20 | 100.0% | 29.1% | 2026-06-15 | 2026-07-22 |
| `lolegaon` | 11 / 20 | 100.0% | 29.1% | 2026-06-15 | 2026-07-22 |
| `rishop` | 11 / 20 | 100.0% | 29.1% | 2026-06-15 | 2026-07-22 |

**Least Covered Destination**: All 6 destinations are currently tied at `11` rows.

---

## 4. Accumulation Projection

- **Remaining ML-eligible rows to reach 180**: `114` rows.
- **Remaining rows per destination to reach 20**: `9` rows per destination ($6 \times 9 = 54$ rows minimum).
- **Current Capture Rate**: `6` canonical destinations per calendar day.
- **Minimum Theoretical Calendar Days**:
  $$\max\left(\left\lceil \frac{114}{6} \right\rceil, 9\right) = 19 \text{ calendar days}$$
- **Status**: `PROJECTED` (Subject to genuine live telemetry availability and source health).
