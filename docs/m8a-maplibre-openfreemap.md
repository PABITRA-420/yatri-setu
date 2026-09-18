# YATRI SETU — MILESTONE 8A: MAPLIBRE + OPENFREEMAP + ROUTING-READY ARCHITECTURE

**System Version**: 0.1.0  
**Milestone**: M8A  
**Target Region**: Eastern Himalayas (Darjeeling, Kalimpong, Lava, Lolegaon, Rishop, Mirik)  

---

## 1. Executive Summary & Judge Explanation

> [!IMPORTANT]
> **Authoritative Decision Boundary Statement**:  
> *"MapLibre/OpenFreeMap provides the map visualization. Routing provides road travel information. Traffic is a separate operational signal. Yatri Setu combines these inputs with its own deterministic crowd, capacity and safety logic; the map provider does not decide the recommended destination."*

Yatri Setu Milestone 8A introduces an open-source, vendor-independent map visualization and road routing architecture, replacing proprietary map dependency (e.g., Google Maps APIs) with:
1. **MapLibre GL JS**: High-performance WebGL client-side map rendering.
2. **OpenFreeMap Liberty Style**: Zero-API-key vector tiles with typography and terrain styling tuned for mountain circuits.
3. **Pluggable Routing Provider Layer**: OSRM (OpenStreetMap live road routing) with seamless Demo and Haversine fallback cascades.
4. **Isolated M7C/M7D Operational Core**: Dynamic crowd pressure (M7C), destination network corridors (M7D), and real-time corridor access disruptions operate deterministically and are never overridden by map display layers.

---

## 2. Architecture Overview

```
                      +---------------------------------------+
                      |         Interactive Map Layer         |
                      |   MapLibre GL JS + OpenFreeMap Liberty|
                      +-------------------+-------------------+
                                          |
                                          v
+------------------------+    +------------------------+    +------------------------+
|    Routing Provider    |    |    Traffic Provider    |    |   M7C / M7D Decision   |
| (OSRM / Demo / Fallback)|    | (Real / Demo / Stale)  |    |     Engine (Core)      |
+-----------+------------+    +-----------+------------+    +-----------+------------+
            |                             |                             |
            | Road Distance / Geometry    | Congestion & Access Status  | Crowd Pressure & Cap.
            v                             v                             v
+------------------------------------------------------------------------------------+
|                   Yatri Setu Unified Route & Destination Advisor                   |
|  - High-precision road corridor tracing                                            |
|  - Real road distance & realistic mountain travel ETA                              |
|  - Canonical OpenWeather observations for target alternative                       |
|  - Strict data provenance tags on every metric                                     |
+------------------------------------------------------------------------------------+
```

---

## 3. Why MapLibre GL JS?

- **Zero Vendor Lock-in**: Open-source fork of Mapbox GL JS maintained by the MapLibre Foundation under the BSD 3-Clause license.
- **Client-side WebGL Performance**: Renders vector tiles, 3D terrain pitch, and dynamic line overlays at 60 FPS without high client memory overhead.
- **Next.js & SSR Compatibility**: Packaged via npm (`maplibre-gl`), cleanly isolated to browser runtime through client-side lifecycle hooks.
- **Zero Paid Token Consumption**: Eliminates the high per-load and per-tile pricing models of Google Maps Platform.

---

## 4. Why OpenFreeMap?

- **Zero API Key Requirement**: Eliminates client credential exposure in `NEXT_PUBLIC_*` environment variables.
- **Liberty Style Aesthetic**: A clean, balanced vector style featuring high-contrast contours, subtle natural shades, and clear road hierarchies that harmonize with Yatri Setu's luxury travel editorial design.
- **Community-Powered OpenStreetMap Data**: Uses global OpenStreetMap vector tiles, ensuring high fidelity across Himalayan mountain roads (Hill Cart Road, Peshok Tea Estate pass, Teesta River crossings).
- **Public Demonstration Notice**: *OpenFreeMap's public instance is provided without an enterprise SLA and is suitable for prototype, evaluation, and hackathon demonstration use.*

---

## 5. Routing Architecture & Provider Abstraction

Routing is decoupled from visual map rendering via the backend `BaseRoutingProvider` abstraction:

```
                  BaseRoutingProvider (ABC)
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
  OSRMRouteProvider   DemoRouteProvider   FallbackRouteProvider
    (OpenStreetMap)     (Curated Corridors)  (Haversine Proximity)
```

### 5.1 Provider Cascade
1. **OSRMRouteProvider** (`provider="osrm"`):
   - Queries OpenStreetMap's public OSRM driving engine (`https://router.project-osrm.org/route/v1/driving/...`).
   - Enforces a strict 3.5s timeout.
   - Extracts road distance (meters to km), travel duration, and GeoJSON LineString coordinates.
   - Provenance: `REAL — OSRM (OPENSTREETMAP)`.
2. **DemoRouteProvider** (`provider="demo"`):
   - Features curated Himalayan road corridors connecting Darjeeling, Kalimpong, Lava, Lolegaon, Rishop, and Mirik.
   - Includes real arterial waypoints (Ghoom, Jorebungalow, Peshok Estate, Teesta Bazaar, Algarah, Sukhia Pokhari).
   - Provenance: `DEMO MODE — SYNTHETIC DATA`.
3. **FallbackRouteProvider** (`provider="fallback"`):
   - Active when road routing servers are unreachable or offline.
   - Employs Yatri Setu's mathematical `haversine_distance_km` straight-line calculation.
   - **Crucial Honesty Rule**: Clearly flags `is_road_distance: false` and labels distance as `Approximate straight-line geographic distance (Haversine)`.
   - Provenance: `FALLBACK — ROUTING UNAVAILABLE (HAVERSINE GEOGRAPHIC ESTIMATE)`.

### 5.2 Routing Endpoint Schema
```json
{
  "origin_destination_id": "darjeeling",
  "origin_name": "Darjeeling",
  "destination_destination_id": "kalimpong",
  "destination_name": "Kalimpong",
  "distance_km": 50.0,
  "duration_minutes": 110,
  "route_geometry": {
    "type": "LineString",
    "coordinates": [[88.2663, 27.0410], ..., [88.4695, 27.0594]]
  },
  "provider": "demo",
  "fetched_at": "2026-09-18T10:15:00Z",
  "provenance_label": "DEMO MODE — SYNTHETIC DATA",
  "is_road_distance": true,
  "transit_mode": "Shared Himalayan Jeep (Peshok Route)",
  "road_condition": "Scenic descent via Peshok Tea Estate down to Teesta Bridge...",
  "traffic_condition": "NORMAL (OPEN)"
}
```

---

## 6. Traffic & Weather Isolation

### 6.1 Map is NOT Traffic
- OpenFreeMap does not supply live vehicular traffic.
- Traffic data is queried independently from Yatri Setu's M7C `TrafficService` (`TRAFFIC_PROVIDER=demo | tomtom | unavailable`).
- The interactive map displays the road path and decorates it with traffic conditions, but the traffic signal originates strictly from the backend traffic snapshot.

### 6.2 Canonical Weather Integrity
- Destination alternative popups and cards display real or cached observations from Yatri Setu's canonical weather engine (`AlternativeWeather`).
- Generic weather defaults (e.g. static "16°C, Clear") remain strictly banned.

---

## 7. Data Provenance & Trust Matrix

| Component | Source / Provider | Provenance Label |
|---|---|---|
| Map Tiles | OpenFreeMap Liberty | `REAL — OPENFREEMAP (LIBERTY)` |
| Map Engine | MapLibre GL JS | `CLIENT — MAPLIBRE GL JS v6.10` |
| Road Routing | OSRM / Curated Demo | `REAL — OSRM (OPENSTREETMAP)` / `DEMO MODE — SYNTHETIC DATA` |
| Proximity Fallback | Haversine Formula | `FALLBACK — ROUTING UNAVAILABLE (HAVERSINE GEOGRAPHIC ESTIMATE)` |
| Destination Weather | OpenWeather / Telemetry Cache | `REAL — OPENWEATHER` / `CACHED — OPENWEATHER` |
| Traffic Signals | M7C Traffic Service | `DEMO MODE — SYNTHETIC DATA` (or `REAL — ARTERIAL TELEMETRY`) |

---

## 8. Security & Privacy

1. **Zero Client Secrets**: No API keys or access tokens are present in `NEXT_PUBLIC_*` bundles for map rendering.
2. **Zero PII Exposure**: Routing queries transmit only destination identifiers (`origin=darjeeling&destination=kalimpong`), avoiding user device coordinates or private home addresses.
3. **Safe Backend Fallback**: Provider timeouts and exceptions are caught and sanitized, returning structured HTTP status codes rather than leaking internal stack traces.

---

## 9. Verification & Test Results

- **Backend Pytest Suite**: 311 passed, 1 skipped.
- **Frontend TypeScript Check**: `npx tsc --noEmit` exited with code 0 (clean compilation).
- **Frontend Production Build**: `npm run build` compiled all routes cleanly with zero WebGL/SSR hydration mismatches.
