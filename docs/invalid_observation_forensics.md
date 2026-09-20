# Invalid Observation Forensic Audit

**Milestone**: Prompt 8 / Branch `v8`  
**System**: Yatri Setu Historical Tourism Data Foundation  
**Auditor**: Historical Observation Quality Engine & Forensic Repair Pipeline  

---

## 1. Forensic Summary & Executive Overview

Prior to Prompt 8, the REAL historical dataset reported:
```text
Total REAL rows: 10
HIGH: 1
MEDIUM: 0
LOW: 5
INVALID: 4
```

This forensic investigation audited all **4 INVALID observations** to determine the precise causal factors for their failure, assess underlying PostgreSQL evidence, and classify them according to the strict Prompt 8 Repair Policy.

### High-Level Forensic Verdict
* **Total INVALID records investigated**: 4
* **Repairable from Genuine Source**: 0
* **Unrepairable (Future Date Bucket)**: 4
* **Silently Deleted**: 0 (Strict policy: unrepairable observations must be preserved in the audit trail)
* **Underlying Source Evidence Available for Future Dates**: None (No bookings or demand events were scheduled or transacted for these future dates)

---

## 2. Granular Forensic Dossier (Per-Observation Breakdown)

### Dossier 1: `lolegaon_2026-09-22_real`
* **Observation ID**: `lolegaon_2026-09-22_real`
* **Destination**: `lolegaon` (Canonical: Yes)
* **Observed At**: `2026-09-20T10:30:00Z`
* **Date Bucket**: `2026-09-22`
* **Ingested At**: `2026-09-20T10:30:15Z`
* **Dataset Mode**: `REAL`
* **Quality Classification**: `INVALID`
* **Validation Error**: `date_bucket '2026-09-22' is in the future.`
* **Missing Target**: False (`current_crowd_pressure = 19.3`)
* **Future Date Bucket**: True (Bucket `2026-09-22` is +2 days ahead of current reference date `2026-09-20`)
* **Missing Provenance**: False (Contains arterial traffic reading from 2026-09-20 mistakenly assigned to future date)
* **Duplicate**: False
* **Invalid Timestamp**: True (observed_at on 2026-09-20 contradicts date_bucket 2026-09-22)
* **Original First-Party Source Records on 2026-09-22**:
  * Bookings: 0
  * Demand Events: 0
* **Repair Classification**: `NOT_REPAIRABLE_FUTURE_BUCKET`
* **Repairable**: `False`
* **Disposition**: Retained in database with provenance audit classification `NOT_REPAIRABLE_FUTURE_BUCKET`. Preserves ML gate auditability without deleting historical rows.

---

### Dossier 2: `mirik_2026-09-25_real`
* **Observation ID**: `mirik_2026-09-25_real`
* **Destination**: `mirik` (Canonical: Yes)
* **Observed At**: `2026-09-20T10:30:00Z`
* **Date Bucket**: `2026-09-25`
* **Ingested At**: `2026-09-20T10:30:15Z`
* **Dataset Mode**: `REAL`
* **Quality Classification**: `INVALID`
* **Validation Error**: `date_bucket '2026-09-25' is in the future.`
* **Missing Target**: False (`current_crowd_pressure = 18.0`)
* **Future Date Bucket**: True (Bucket `2026-09-25` is +5 days ahead of current reference date `2026-09-20`)
* **Missing Provenance**: False (Contains traffic reading from 2026-09-20 mapped to future bucket)
* **Duplicate**: False
* **Invalid Timestamp**: True (observed_at on 2026-09-20 contradicts date_bucket 2026-09-25)
* **Original First-Party Source Records on 2026-09-25**:
  * Bookings: 0
  * Demand Events: 0
* **Repair Classification**: `NOT_REPAIRABLE_FUTURE_BUCKET`
* **Repairable**: `False`
* **Disposition**: Retained in database with provenance audit classification `NOT_REPAIRABLE_FUTURE_BUCKET`.

---

### Dossier 3: `kalimpong_2026-10-01_real`
* **Observation ID**: `kalimpong_2026-10-01_real`
* **Destination**: `kalimpong` (Canonical: Yes)
* **Observed At**: `2026-09-20T08:00:00Z`
* **Date Bucket**: `2026-10-01`
* **Ingested At**: `2026-09-20T08:00:05Z`
* **Dataset Mode**: `REAL`
* **Quality Classification**: `INVALID`
* **Validation Error**: `date_bucket '2026-10-01' is in the future.`
* **Missing Target**: False (`current_crowd_pressure = 10.0`)
* **Future Date Bucket**: True (Bucket `2026-10-01` is +11 days ahead of current reference date `2026-09-20`)
* **Missing Provenance**: True (Empty provenance `{}`)
* **Duplicate**: False
* **Invalid Timestamp**: True (Telemetry timestamp misalignment)
* **Original First-Party Source Records on 2026-10-01**:
  * Bookings: 0
  * Demand Events: 0
* **Repair Classification**: `NOT_REPAIRABLE_FUTURE_BUCKET`
* **Repairable**: `False`
* **Disposition**: Retained in database with provenance audit classification `NOT_REPAIRABLE_FUTURE_BUCKET`.

---

### Dossier 4: `kalimpong_2026-10-02_real`
* **Observation ID**: `kalimpong_2026-10-02_real`
* **Destination**: `kalimpong` (Canonical: Yes)
* **Observed At**: `2026-09-20T08:00:00Z`
* **Date Bucket**: `2026-10-02`
* **Ingested At**: `2026-09-20T08:00:05Z`
* **Dataset Mode**: `REAL`
* **Quality Classification**: `INVALID`
* **Validation Error**: `date_bucket '2026-10-02' is in the future.`
* **Missing Target**: False (`current_crowd_pressure = 10.0`)
* **Future Date Bucket**: True (Bucket `2026-10-02` is +12 days ahead of current reference date `2026-09-20`)
* **Missing Provenance**: True (Empty provenance `{}`)
* **Duplicate**: False
* **Invalid Timestamp**: True (Telemetry timestamp misalignment)
* **Original First-Party Source Records on 2026-10-02**:
  * Bookings: 0
  * Demand Events: 0
* **Repair Classification**: `NOT_REPAIRABLE_FUTURE_BUCKET`
* **Repairable**: `False`
* **Disposition**: Retained in database with provenance audit classification `NOT_REPAIRABLE_FUTURE_BUCKET`.

---

## 3. Repair Policy Enforcement & Non-Deletion Rationale

### Why These Records Were NOT Repaired to Past Dates
Prompt 8 Section 6 establishes that an observation may **only** be repaired if the original genuine source data exists and supports the corrected value:
* In all 4 cases, there were no underlying bookings, search demand events, or verified footfall observations intended for those dates that were misplaced.
* Shifting these observations backward to `2026-09-20` would create duplicate rows or overwrite real-time telemetry.
* Interpolating, guessing, or using synthetic generators is strictly forbidden (Prompt 8 Section 7).

### Why These Records Were NOT Deleted
Prompt 8 Section 33 mandates:
> **"If an observation is genuinely invalid: Do not simply delete it because that would make INVALID = 0. Instead: retain audit history, preserve original evidence, repair only when justified, mark unrepairable observations explicitly."**

Deleting invalid rows simply to report zero invalid observations would represent academic dishonesty and compromise dataset lineage. By retaining them with explicit `NOT_REPAIRABLE_FUTURE_BUCKET` audit stamps, the ML gate accurately accounts for their presence and prevents synthetic or unverified rows from qualifying for production.

---

## 4. Administrative Repair & Forensic Verification API

The system exposes programmatic access for continuous inspection:
* `GET /api/v1/historical/forensics`: Returns the dynamic forensic dossier for all invalid observations.
* `POST /api/v1/historical/repair-invalid`: Executes idempotent evidence-backed repair runs with `dry_run` support.
* `GET /api/v1/admin/historical/forensics`: Admin Command Center authenticated mirror.
