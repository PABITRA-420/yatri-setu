# Data Provenance Audit & Isolation Report

## Executive Summary
This document provides a comprehensive audit, classification, and architectural isolation of all **MOCK**, **SYNTHETIC**, **DEMO**, **HARDCODED**, and **FALLBACK** data across the Yatri Setu platform. 

The primary objective is to ensure that **synthetic, calibrated baseline, or demo values are NEVER misrepresented as genuine live or historical observations**, while preserving deterministic fixtures required for automated tests, offline resilience, and local development.

---

## 1. Provenance Classification Taxonomy

Every data stream and component across Yatri Setu is classified into one of seven canonical tiers:

| Classification | Definition | Example in Yatri Setu |
|---|---|---|
| **`LIVE`** | Genuine, real-time telemetry obtained via verified active provider APIs. | OpenWeather live temperature & humidity (`LIVE_OPENWEATHERMAP_API`), TomTom corridor traffic speeds (`REAL_TOMTOM_FLOW`). |
| **`CACHED`** | Previously fetched genuine observations stored in local TTL memory/redis. Valid unexpired cache. | Unexpired OpenWeather or TomTom observation within 5–15 min TTL window. |
| **`HISTORICAL`** | Genuine past data recorded from real operational events or verified government archives. | Authenticated first-party Yatri Setu booking events stored in PostgreSQL `bookings` table. |
| **`COMPUTED`** | Deterministically derived or aggregated metrics from verified multi-source input signals. | Canonical Crowd Pressure Score from `crowd_engine_v2`, Haversine distance, capacity utilization. |
| **`SYNTHETIC`** | Programmatically simulated multi-signal datasets generated from regional domain models for ML training and benchmarking. | Milestone 6A deterministic 365-day dataset (`app/data/historical_dataset.py`). |
| **`DEMO`** | Seeded prototype profiles, curated regional benchmarks, and presentation mockups. | Curated homestay profiles (`seed_data.py`), similarity target calibrations (e.g. 87% Kalimpong match). |
| **`UNAVAILABLE`** | Explicit degraded state when real provider fails and no valid cache exists. No numerical value manufactured. | Provider offline signal, `data_quality="DEGRADED"`, `confidence=0.0`. |

---

## 2. Comprehensive Provenance Audit Matrix

| Component | Current Source | Classification | Production Safe? | Action Taken / Isolation Mechanism |
|---|---|---|---|---|
| **Live Weather Telemetry** | OpenWeather API (`weather_real_provider.py`, `weather/service.py`) | `LIVE` (when key set) / `CACHED` / `DEMO` | Yes (Safe) | If key present, queries OpenWeather API. Unexpired results marked `CACHED`. Stale cache marked `STALE` with degraded confidence. Demo simulator marked `DEMO MODE — SYNTHETIC DATA`. |
| **Live Corridor Traffic** | TomTom Traffic Flow API (`traffic/service.py`, `traffic_data.py`) | `LIVE` (when key set) / `CACHED` / `DEMO` | Yes (Safe) | If key present, queries TomTom routing/flow. Stale cache marked `REAL — TOMTOM (STALE CACHE)`. No-cache fallback marked `DEMO MODE — SYNTHETIC DATA` and never cached as real. |
| **Canonical Crowd Engine V2** | Multi-signal weighted aggregator (`crowd_engine_v2.py`) | `COMPUTED` | Yes (Safe) | Canonical source of truth for current pressure. Computes dynamic weighted sum of available signals; renormalizes weights when signals are missing; lowers confidence rather than manufacturing missing signals. |
| **Legacy Crowd Engine V1** | Hardcoded factor weights (`crowd_engine.py`) | `DEMO` / `HISTORICAL` | Deprecated (Safe) | Marked deprecated with `DeprecationWarning`. Preserved strictly for backward unit test verification. Runtime services migrated to V2. |
| **Tourism Footfall Signal** | Regional seasonal profiles (`tourism_data.py`, `tourism_ingestor.py`) | `SYNTHETIC` | Yes (Isolated) | Explicitly labeled `MOCK:tourism_historical` and `Mock Tourism Simulator (WBTDC Analog)`. Notes explicitly clarify: *No live state tourism board API exists for these micro-destinations*. |
| **Accommodation Occupancy** | Yatri Setu network listings (`accommodation_data.py`) | `DEMO` / `COMPUTED` | Yes (Isolated) | Clearly labeled `MOCK: Yatri Setu network occupancy` with `is_nationwide=False`. Explains it tracks registered network capacity rather than statewide hotel statistics. |
| **Booking Demand Signal** | PostgreSQL `bookings` table (`booking_demand.py`) | `HISTORICAL` / `LIVE` / `DEMO` | Yes (Safe) | Checks PostgreSQL `confirmed` bookings. When DB has records, labeled `POSTGRESQL_BOOKING_TELEMETRY` (`REAL`). When empty, falls back to calibrated velocity baseline labeled `MOCK_BOOKING_INTAKE_ENGINE`. |
| **Search Demand Signal** | Leading travel intent model (`search_demand.py`, `demand_aggregation_service.py`) | `COMPUTED` / `SYNTHETIC` | Yes (Safe) | First-party searches recorded in `demand_aggregation_service`. Provider explicitly labeled `MOCK_SEARCH_DEMAND_LEADING_INDEX`. |
| **Conversion Funnel** | First-party demand events (`funnel_service.py`) | `COMPUTED` / `HISTORICAL` | Yes (Refactored) | **Removed arbitrary multiplier formulas** (`searches * 0.45`, `alt_views * 0.22`, `alt_accepts * 0.8`). Funnel now reports **genuine observed event counts** from the database/ledger. |
| **ML Training Dataset** | 365-day generated observations (`historical_dataset.py`) | `SYNTHETIC` | Yes (Isolated) | Records labeled `SYNTHETIC_GENERATOR` with fixed RNG seed (42). Header carries transparency notice: *Synthetic demo observations for ML benchmarking; never presented as real sensor readings*. |
| **XGBoost Forecasting** | Trained gradient boosted model (`ml_forecast.py`) | `COMPUTED` | Yes (Safe) | Separate future forecasting layer (1 to 14 days). Consumes canonical current pressure as an input feature and outputs multi-horizon projections with feature importance. |
| **Alternative Similarity Calibration** | Multi-attribute formula + calibration targets (`alternative_engine.py`) | `DEMO` | Yes (Classified) | Added explicit `similarity_provenance="DEMO_CALIBRATION_BENCHMARK"` to response model so the 87% / 85% / 81% regional benchmarks are never claimed to be live sensor measurements. |
| **OSRM vs Haversine Distance** | Routing service (`routing_service.py`, `alternative_engine.py`) | `COMPUTED` | Yes (Safe) | Explicitly distinguishes `distance_provenance`: `"OSRM_ROAD_DISTANCE"` vs `"HAVERSINE_GEOGRAPHIC_ESTIMATE"`. |
| **Homepage Sanctuaries & Ticker** | Frontend homepage (`page.tsx`) | `LIVE` / `COMPUTED` (Fallback: `DEMO`) | Yes (Refactored) | Homepage now dynamically fetches `fetchDestinations()` (`GET /api/destinations`) to render live canonical V2 crowd scores in the ticker and cards. Retains `DEFAULT_TICKER` and `sampleDestinations` strictly as offline fallbacks. |
| **Tourist Dashboard** | Tourist identity, booking ref, credits (`dashboard/page.tsx`) | `DEMO` | Presentation Only | Preserved as a prototype demo UI ("Aarav Sharma", ref "YS-BK-7492A", 30 Green Credits). Documented future production endpoints: `/api/v1/auth/me`, `/api/v1/bookings/{id}`, `/api/v1/rural/rewards/{id}`. |
| **Frontend API Fallback Constants** | Seed constants (`frontend/src/lib/api.ts`) | `DEMO` (Offline Fallback) | Yes (Isolated) | `FALLBACK_DESTINATIONS`, `FALLBACK_HOMESTAYS`, and fallback crowd data are invoked **only on network catch**. Logged with `console.warn` for transparency and preserved for offline/test reliability. |

---

## 3. Detailed Audit Findings & Remediation

### 3.1 Arbitrary Formulas Removed
- **Previous state**: In [`funnel_service.py`](file:///d:/yatri-setu/backend/app/services/conversion/funnel_service.py), when zero demand events were recorded, the funnel manufactured synthetic numbers using hardcoded multipliers:
  - `alt_views = int(searches * 0.45)`
  - `alt_accepts = int(alt_views * 0.22)`
  - `avail_checks = int(alt_accepts * 0.8)`
  - `booking_inits = int(avail_checks * 0.5)`
  - `booking_confirms = int(booking_inits * 0.75)`
- **Remediation**: All arbitrary multiplier formulas have been **completely eliminated**. `funnel_service.py` now reports genuine observed counts from the demand event database. If no events exist, the count is truthfully 0.

### 3.2 Provider Failure & Graceful Degradation
- **Previous state**: In [`base.py`](file:///d:/yatri-setu/backend/app/services/data_sources/base.py), `DataSourceReading.__post_init__` forcibly clamped `provider_mode` to `("MOCK", "REAL", "CACHED")`, rewriting `"UNAVAILABLE"` to `"MOCK"`.
- **Remediation**: Expanded `VALID_PROVIDER_MODES` to include `("REAL", "LIVE", "CACHED", "HISTORICAL", "COMPUTED", "SYNTHETIC", "DEMO", "MOCK", "UNAVAILABLE")`. When a provider is unreachable and no valid cache exists, it cleanly returns `provider_mode="UNAVAILABLE"` with `confidence=0.0`.

### 3.3 Alternative Recommendation Similarity Provenance
- **Previous state**: In [`alternative_engine.py`](file:///d:/yatri-setu/backend/app/services/alternative_engine.py), similarity scores for Darjeeling alternatives (87% Kalimpong, 85% Rishop, 81% Lava, etc.) were hardcoded demo calibrations but returned without explicit provenance metadata.
- **Remediation**: Added `similarity_provenance: Optional[str] = "DEMO_CALIBRATION_BENCHMARK"` to [`AlternativeRecommendation`](file:///d:/yatri-setu/backend/app/models/crowd.py) and populated it explicitly. This preserves test determinism while establishing transparent classification.

### 3.4 Homepage Sample Destinations & Live API Integration
- **Previous state**: [`frontend/src/app/page.tsx`](file:///d:/yatri-setu/frontend/src/app/page.tsx) rendered static hardcoded crowd scores (Darjeeling 88, Kalimpong 42, Lava 24, etc.) in the Live Regional Crowd Density Ticker and Curated Sanctuaries cards.
- **Remediation**: Connected `page.tsx` to `fetchDestinations()` via `useEffect`. When the backend API is reachable, the homepage dynamically updates with live canonical V2 crowd scores (`crowd_score`, `crowd_level`, and tags) from `GET /api/destinations`. The hardcoded arrays are retained strictly as offline fallback fixtures, with zero UI styling or visual changes.

### 3.5 Tourist Dashboard Identity & Green Credits
- **Audit Finding**: In [`frontend/src/app/dashboard/page.tsx`](file:///d:/yatri-setu/frontend/src/app/dashboard/page.tsx), traveler identity ("Aarav Sharma"), booking reference ("YS-BK-7492A"), and "30 Green Credits" are currently hardcoded for the Smart India Hackathon (SIH 2026) prototype demonstration.
- **Classification**: **`DEMO`** (Presentation Prototype).
- **Target Backend APIs (for future milestone)**:
  1. Traveler Identity: `GET /api/v1/auth/me` or `/api/v1/tourist/profile`
  2. Active Journey / Pass: `GET /api/v1/trips/{trip_id}` or `/api/v1/bookings/active`
  3. Green Credits Ledger: `GET /api/v1/rural/rewards/{user_id}`
- **Action**: Per user constraint, the dashboard was not redesigned in this prompt.

---

## 4. Verification Summary

### Automated Test Suite
- Executed: `python -m pytest`
- Results: **345 passed, 1 skipped, 0 failed** in 106.36 seconds.
- Dedicated isolation test file added: [`backend/tests/test_data_provenance_isolation.py`](file:///d:/yatri-setu/backend/tests/test_data_provenance_isolation.py) (13 tests verifying synthetic data availability, non-labeling of mocks as live, unavailable/stale cache behavior, similarity provenance, and elimination of arbitrary multiplier formulas).

### Frontend Production Build
- Executed: `npm run build` in `frontend/`
- Results: **Compiled 21 static and dynamic routes in 10.9s with 0 errors**.
- Zero layout, styling, typography, color, or component changes introduced (UI strictly locked).
