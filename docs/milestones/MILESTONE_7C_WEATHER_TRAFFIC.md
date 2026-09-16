# Milestone 7C: Live Weather + Traffic Intelligence & Dynamic Pressure Recalculation

## Overview
Milestone 7C integrates real-time meteorological intelligence, arterial corridor traffic delay anomalies, and causal multi-signal pressure recalculation into Yatri Setu. It enables the platform to react dynamically to changing mountain conditions across the Darjeeling–Kalimpong–Neora Valley Himalayan tourism circuit.

---

## Architecture & Guarantees

### 1. Dual-Track Provider Architecture
- **Weather Intelligence (`backend/app/services/weather/`)**:
  - `BaseWeatherProvider` interface.
  - `DemoWeatherProvider`: High-fidelity deterministic simulator with rich profiles across all 6 destinations (Tiger Hill Kanchenjunga visibility, Teesta gorge winds, Neora mist).
  - `OpenWeatherProvider`: Production caller with timeout protection (4s) and rate-limiting.
  - `UnavailableWeatherProvider`: Fail-safe fallback.
  - In-memory 15-minute TTL caching with graceful stale-fallback logic.
  - Deterministic weather impact calculation: maps meteorological metrics into an impact score $[-1.0, +1.0]$.

- **Traffic Intelligence (`backend/app/services/traffic/`)**:
  - `BaseTrafficProvider` interface.
  - `DemoTrafficProvider`: Arterial mountain corridors for all 6 destinations:
    - Darjeeling: NH-55 (Hill Cart Road), Rohini Mountain Toll Bypass, Pankhabari Heritage Route.
    - Kalimpong: NH-10 (Teesta River Corridor), Rishi Road (Pedong Arterial).
    - Lava: Gorubathan–Lava Mountain Pass, Damdim–Algarah Connector.
    - Lolegaon: Lava–Lolegaon Forest Corridor.
    - Rishop: Upper Rishop Eco-Jeep Trail.
    - Mirik: Mirik–Kurseong Ridge Highway, Dudhia–Mirik Foothills Road.
  - Travel-time ratio evaluation: $\text{ratio} = \frac{\text{current\_time}}{\text{historical\_time}}$.
  - Congestion classification: `NORMAL` ($<1.15$), `ELEVATED` ($1.15-1.4$), `HIGH` ($1.4-1.8$), `CRITICAL` ($\ge 1.8$).
  - Decoupled `access_status`: `OPEN`, `CAUTION`, `DISRUPTED`, `UNKNOWN`.

### 2. Pressure Recalculation & Causal Diagnostics (`PressureRefreshService`)
- Multi-Signal Synthesis:
  - Historical Footfall ($w=0.20$)
  - Accommodation Occupancy ($w=0.15$)
  - First-Party Demand Telemetry ($w=0.15$)
  - Corridor Traffic Pressure ($w=0.15$)
  - Event Pressure ($w=0.15$)
  - Holiday / Weekend Pressure ($w=0.10$)
  - Weather Impact ($w=0.10$)
- **Explainable Top Drivers**: Identifies top causal contributors shaping today's pressure score.
- **Delta Tracking ("Why Pressure Changed")**: Snapshots previous refresh states to provide causal delta explanations with point contributions.
- **Future Dates Isolation**: For future dates, weather uses forecast models (`FORECAST CONDITIONS`), and real-time road delays are marked as not applicable without fabricating live telemetry.

### 3. Alternative Recommendation Safety Filter
- If a destination has `access_status == "DISRUPTED"` (roadblock or landslide) or severe weather hazard warnings, `get_alternative_destinations()` automatically filters it out of recommended candidate destinations.

### 4. Strict Provenance & Security
- Provenance labels strictly audit telemetry source:
  - `REAL — LIVE METEOROLOGICAL & CORRIDOR FEEDS`
  - `MIXED — REAL & DEMO CORRIDOR TELEMETRY`
  - `CACHED — TELEMETRY WITH GRACEFUL FALLBACK`
  - `DEMO — SYNTHETIC HIMALAYAN TELEMETRY`
- Secret API keys (`WEATHER_API_KEY`, `TRAFFIC_API_KEY`) are never transmitted to clients or serialized in API responses.
- Manual refresh endpoint (`POST /api/admin/pressure/refresh`) is protected with a 5-second cooldown rate limiter.

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/destinations/{id}/live-weather` | Normalized live weather observation with cache status |
| `GET` | `/api/destinations/{id}/traffic` | Multi-route arterial road telemetry and access status |
| `GET` | `/api/destinations/{id}/conditions` | Comprehensive destination conditions (weather + traffic + pressure) |
| `GET` | `/api/destinations/circuit/conditions` | Unified circuit-wide corridor and weather matrix |
| `GET` | `/api/destinations/{id}/pressure-explanation` | Deterministic explanation of top drivers and deltas |
| `POST` | `/api/admin/pressure/refresh` | Administrative trigger with 5s cooldown rate protection |

---

## Verification
- Backend Unit Tests: `tests/test_milestone7c_weather_traffic.py` (17/17 passed).
- Total Backend Suite: 165/165 passed (zero regressions).
- Frontend TypeScript: `npx tsc --noEmit` passed with 0 errors.
- Production Build: `npm run build` verified.
