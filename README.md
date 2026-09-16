# 🏔️ Yatri Setu (यात्री सेतु)
### Hyperlocal & Rural Tourism Platform with Active Crowd Management & Traveler Safety
**Smart India Hackathon 2026** • Complete Implementation (Milestones 1 through 7H)

---

## 🌟 Core Differentiator
Most commercial travel platforms operate as passive booking engines, exacerbating overtourism by routing thousands of travelers into already saturated hotspots.

**Yatri Setu actively manages tourist flow.** When fragile mountain destinations (such as Darjeeling during peak autumn sunrise/tea season) reach severe congestion, Yatri Setu:
1. **Computes a deterministic crowd index (0–100)** and classifies it as **LOW / MEDIUM / HIGH / VERY HIGH**.
2. **Generates natural language explainability** for why the score is high (e.g. hotel saturation, arterial choke points, scenic viewpoint queue bottlenecks).
3. **Identifies capacity-verified rural alternatives** (e.g. Kalimpong, Lava, Lolegaon, Rishop, Mirik).
4. **Calculates multi-attribute similarity, distance, and cost savings** (e.g. Kalimpong: 87% similarity, 42% cost savings, 50 km away).
5. **Connects travelers to verified rural panchayat homestays** where 90% of revenue goes directly to the rural host and 5% supports local Gram Panchayat village development funds.
6. **Protects travelers with built-in Emergency SOS**, broadcasting GPS telemetry to the regional *Yatri Mitra* volunteer responder network and tourism safety desks, alongside verified direct access to official national helplines (112, 1363, 1091).

---

# Yatri Setu Crowd Intelligence Architecture

Yatri Setu implements an explainable, deterministic multi-engine architecture designed for operational reliability in fragile Himalayan environments.

```
M1 BASELINE
    ↓  Fast deterministic tourist-facing baseline (6 weighted factors)
M7C LIVE RECALCULATION
    ↓  Current / future dynamic pressure using operational telemetry
M7D/M7E FLOW MANAGEMENT
    ↓  Checks whether an alternative is safe, reachable, suitable, and capable of absorbing visitors
M6 XGBOOST
    ↓  Offline predictive benchmark / validation layer (Advisory only; never overrides live serving score)
```

### The Two-Layer Deterministic Model:
- **Layer 1: M1 Tourist Baseline Engine (`crowd_engine.py`)**: Instantaneous, deterministic 0–100 tourist crowd score derived from 6 transparent demographic and geographic factors. Powers tourist browsing, destination badges, and initial flow awareness.
- **Layer 2: M7C Dynamic Live Conditions & Pressure Recalculator (`pressure_refresh_service.py`)**: Ingests real-time operational telemetry (live weather observations, corridor traffic statuses, first-party booking demand, active event schedules, and holiday surges) to recalculate dynamic operational pressure and track refresh cycle deltas.
- **Network & Capacity Layer: M7D Flow Management (`alternative_engine.py`)**: Enforces hard safety, road accessibility, and carrying capacity constraints before candidate destinations can be suggested as alternatives.
- **Validation Layer: M6 XGBoost ML Benchmark (`ml_training_pipeline.py`)**: Supervised gradient boosted regression model evaluated chronologically against the rule engine. **The XGBoost model is a predictive benchmark and validation layer. It does not determine the authoritative tourist-facing crowd score.**

---

## Judge-Ready Crowd Engine Definition

### 1. M1 Base Tourist Crowd Engine (Authoritative Baseline)
- **Engine Type**: Deterministic, serving-layer calculation.
- **Scale**: Normalized integer from 0 to 100.
- **Exact Formula**:
  $$\text{Crowd Score} = 0.35 \times H + 0.25 \times B + 0.15 \times S + 0.10 \times Hol + 0.10 \times W + 0.05 \times T$$
- **Exact Factor Weights**:
  - **Historical Tourist Footfall ($H$)**: **35%** (Multi-year seasonal arrival density).
  - **Hotel & Homestay Booking Density ($B$)**: **25%** (Current accommodation occupancy & reservations).
  - **Seasonal Tourism Index ($S$)**: **15%** (Optimal blooming & mountain visibility window).
  - **Weekend & Holiday Multiplier ($Hol$)**: **10%** (Regional holiday influx from Kolkata/Siliguri).
  - **Clear Sky & Weather Index ($W$)**: **10%** (Mountain visibility triggering spontaneous travel).
  - **Transit Route & Bottleneck Density ($T$)**: **5%** (Arterial mountain road choke point saturation).
- **Exact Classification Thresholds**:
  - `0 – 25`: **LOW** (Emerald Green — Pristine tranquility)
  - `26 – 50`: **MEDIUM** (Amber — Balanced footfall)
  - `51 – 75`: **HIGH** (Orange — Elevated density)
  - `76 – 100`: **VERY HIGH** (Rose Red — Critical congestion alert)

### 2. M7C Dynamic Live Conditions & Pressure Engine
- **Engine Type**: Deterministic dynamic multi-signal recalculator.
- **Scale**: Continuous score from 0.0 to 100.0 with explainable top driver breakdown and delta tracking.
- **Exact Current-Day Weights**:
  - **Historical Footfall Baseline**: **20%**
  - **Accommodation Occupancy**: **15%**
  - **First-Party Demand Telemetry**: **15%**
  - **Corridor Traffic Pressure**: **15%**
  - **Local Event Pressure**: **15%**
  - **Holiday Influx**: **10%**
  - **Live Mountain Weather Impact**: **10%**
  $$\text{Total} = 20\% + 15\% + 15\% + 15\% + 15\% + 10\% + 10\% = 100\%$$
- **Exact Future-Date Weights** (Traffic telemetry not assumed for future dates; nominal baseline used):
  - **Historical Footfall Baseline**: **25%**
  - **Accommodation Occupancy**: **20%**
  - **First-Party Demand Telemetry**: **15%**
  - **Traffic Baseline**: **5%**
  - **Local Event Pressure**: **15%**
  - **Holiday Influx**: **10%**
  - **Weather Forecast Impact**: **10%**
  $$\text{Total} = 25\% + 20\% + 15\% + 5\% + 15\% + 10\% + 10\% = 100\%$$
- **Exact Pressure Classification Thresholds**:
  - `< 40.0`: **LOW**
  - `40.0 – 59.9`: **MODERATE**
  - `60.0 – 79.9`: **HIGH**
  - `≥ 80.0`: **CRITICAL**

### 3. M7D Capacity-Aware Alternative Suitability & Exclusion Rules
- **Exact Capacity Exclusion Threshold**:
  Candidate destinations are **strictly excluded** from receiving redirected tourist flow if:
  $$\text{Capacity Health Status} == \text{FULL} \quad (\text{Occupancy Rate} \ge 90\%) \quad \text{OR} \quad \text{Available Units} \le 0$$
- **Exact Operational Capacity Health Classifications**:
  - `HEALTHY`: Occupancy $< 50\%$
  - `LIMITED`: Occupancy $50\% - 75\%$
  - `HIGH_UTILIZATION`: Occupancy $75\% - 90\%$
  - `FULL`: Occupancy $\ge 90\%$ (Strictly Excluded)
- **Exact Candidate Exclusion Filters** (Executed in strict sequence):
  1. **Network Connectivity**: Route must be topologically connected and active (`destination_network_service`).
  2. **Corridor Access Filter**: Access status must **not** be `DISRUPTED` (`access_status != "DISRUPTED"`).
  3. **Severe Weather Filter**: Severe weather warning must **not** be present (`has_severe_weather == False`).
  4. **Capacity Filter**: Capacity must **not** be `FULL` ($\ge 90\%$ occupancy) and available units must be $> 0$.
  5. **Pressure Filter**: Candidate destination crowd score must be $< 80$ and must **not** exceed the origin crowd score.
- **Exact Alternative Candidate Suitability Scoring**:
  Surviving candidates are ranked deterministically by a 0–100 Suitability Index:
  - **Pressure Suitability**: **35%** ($\max(0, 100 - \text{crowd\_score}) \times 0.35$)
  - **Available Accommodation Capacity**: **25%** ($\text{HEALTHY}=100, \text{LIMITED}=70, \text{HIGH\_UTILIZATION}=40, \text{FULL}=0 \times 0.25$)
  - **Access & Corridor Condition**: **15%** ($\text{OPEN}=100, \text{CAUTION}=60, \text{DISRUPTED}=0 \times 0.15$)
  - **Multi-Attribute Similarity & Proximity**: **15%** ($\text{Cosine Similarity} \times 0.15$)
  - **Weather Condition Suitability**: **10%** ($\text{Normal}=100, \text{Severe}=0 \times 0.10$)
  $$\text{Total} = 35\% + 25\% + 15\% + 15\% + 10\% = 100\%$$

### 4. M6 XGBoost Advisory Benchmark
- **Role**: Offline predictive benchmark and validation layer.
- **Authoritative Status**: Non-authoritative. It never calculates, overrides, or alters the live serving crowd score.
- **Dataset**: Trained on 2023 standardized historical benchmark observations (2,190 rows across 6 Himalayan destinations) and evaluated chronologically on test observations (Nov 1, 2023 – Dec 31, 2023: 366 observations).

---

## 🧭 Core Demo Flow for SIH 2026 Judges

1. **Landing Page (`/`)**:
   - Inspect the regional live crowd ticker.
   - Click **"Launch Darjeeling Demo"** or search "Darjeeling".
2. **Crowd Intelligence Panel (`/destinations/darjeeling/crowd`)**:
   - View the circular gauge showing **VERY HIGH 88/100**.
   - Read the explainability bullet points ("Why is it crowded?").
   - Review the 6 factor breakdown progress bars.
   - Click **"View Suggested Alternatives"**.
3. **Suggested Alternatives Advisor (`/destinations/darjeeling/alternatives`)**:
   - Note **Kalimpong** ranked as top suggested alternative with **87% Similarity**, **42/100 (Medium Crowd)**, and **42% Cost Savings**.
   - Review the Access Status (`OPEN`), Weather (`Clear, 16°C`), and Capacity (`HEALTHY`).
   - Click **"Choose Kalimpong & Generate Itinerary"**.
4. **AI Itinerary Planner (`/itinerary?destination=kalimpong`)**:
   - Inspect the crowd-avoidance rating: *"91% Overcrowding Avoided"*.
   - Browse Day 1, Day 2, and Day 3 timeline tabs with morning/afternoon/evening slots.
   - Click **"Select Verified Homestay"**.
5. **Homestays (`/homestays?destination_id=kalimpong`)**:
   - Inspect *Pineview Orchid Retreat & Homestay* (Panchayat Verified, 90% Host Retention, 5% Gram Panchayat Village Fund).
   - Click **"Reserve Stay"**.
6. **Booking Confirmation (`/booking/confirmation`)**:
   - Confirm booking to generate the **Digital Travel Pass QR**.
   - Click **"Go to Active Trip Dashboard"**.
7. **Active Trip Dashboard (`/trips/YS-BK-...`)**:
   - Review packing checklist, weather advisory, and digital travel pass.
   - Access emergency assistance.
8. **SOS Safety Screen (`/safety/sos`)**:
   - Click the red **"HOLD SOS"** button.
   - Watch the screen activate into an emergency distress broadcast with GPS coordinates (`27.0667° N, 88.4667° E`), verified *Yatri Mitra* community responder coordination, and immediate direct-dial access to official national helplines (112, 1363, 1091).
9. **Admin Command Center (`/admin/command-center`)**:
   - Review macro circuit metrics, live traffic corridor monitors, weather telemetry provenance badges, capacity health statuses, and the XGBoost advisory benchmark evaluation.

---

## 🗂️ Architecture & Folder Structure

```
yatri-setu/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point with CORS, rate limiting & health checks
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic settings & database URL normalizer
│   │   │   ├── rate_limit.py           # Thread-safe in-memory sliding window rate limiter
│   │   │   └── logging.py              # Log sanitation scrubbing secrets & tokens
│   │   ├── data/
│   │   │   └── seed_data.py            # Curated seed data for 6 Himalayan destinations
│   │   ├── models/                     # Pydantic & SQLAlchemy domain schemas
│   │   ├── services/
│   │   │   ├── crowd_engine.py         # M1 Deterministic 6-factor crowd calculation
│   │   │   ├── alternative_engine.py   # M7D Capacity-aware flow & suitability ranking
│   │   │   ├── pressure_refresh_service.py # M7C Dynamic multi-signal pressure recalculation
│   │   │   ├── destination_network_service.py # M7D Route graph & corridor feasibility
│   │   │   ├── capacity/               # M7D Accommodation inventory & health service
│   │   │   ├── weather/                # M7C/M7H OpenWeather & demo weather providers
│   │   │   ├── traffic/                # M7C Corridor traffic & access monitor
│   │   │   ├── ml_training_pipeline.py # M6 XGBoost supervised regression benchmark
│   │   │   ├── safety/                 # M7F SOS service, responders & national directory
│   │   │   └── itinerary_service.py    # M2B/M7H Adaptive itinerary engine (Mock / OpenAI)
│   │   └── api/v1/                     # Consolidated REST API endpoints
│   └── tests/                          # Automated Pytest suite (236 tests passing)
├── frontend/
│   ├── src/
│   │   ├── app/                        # Next.js App Router (21 production routes)
│   │   ├── components/                 # Reusable UI components & visual gauges
│   │   ├── lib/                        # API client with offline fallback & utils
│   │   └── types/                      # TypeScript definitions aligned with backend
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

---

## 🛰️ Strict Telemetry Provenance Taxonomy

Yatri Setu strictly separates verified production signals from simulated planning models. Every signal carries explicit provenance:

| Provenance Label | Meaning & Usage |
| :--- | :--- |
| `REAL — EXTERNAL PROVIDER` | Live observations fetched from verified external APIs (e.g. OpenWeatherMap API). |
| `REAL — YATRI SETU NETWORK` | Verified first-party transactions, homestay bookings, and search telemetry from the platform. |
| `MIXED — STALE TELEMETRY FALLBACK` | Cached live observations served when upstream providers exceed timeout thresholds. |
| `DEMO MODE — SYNTHETIC DATA` | High-fidelity deterministic Himalayan mountain simulation used when external keys are unconfigured. |
| `SIMULATED — PLANNING SCENARIO` | Hypothetical flow redistribution calculations used by administrative macro planners. |

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ (Tested on v22.x)
- npm 9+

### 1. Start the FastAPI Backend
```bash
# In project root:
pip install -r backend/requirements.txt

# Run full automated test suite (236 tests):
$env:PYTHONPATH="backend"; python -m pytest backend/tests

# Launch FastAPI development server (port 8000):
$env:PYTHONPATH="backend"; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Health Check: `http://127.0.0.1:8000/health`
- Interactive OpenAPI Documentation: `http://127.0.0.1:8000/docs`

### 2. Start the Next.js Frontend
```bash
# In a new terminal, navigate to the frontend directory:
cd frontend

# Verify TypeScript types:
npx tsc --noEmit

# Start development server (port 3000):
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🔐 Environment Configuration Template

Key configuration options supported by `backend/.env` (see `backend/.env.example` for template):

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Runtime mode (`development`, `staging`, `production`) |
| `DATABASE_URL` | `sqlite:///./yatri_setu.db` | PostgreSQL or local SQLite URI (auto-normalizes `postgres://` for SQLAlchemy 2.0) |
| `WEATHER_PROVIDER` | `openweather` | Weather source (`openweather`, `demo`, `unavailable`) |
| `WEATHER_API_KEY` | `""` | OpenWeatherMap API key (backend-only; never exposed to browser) |
| `AI_PROVIDER` | `mock` | Natural language itinerary assistance (`mock`, `openai`, `claude`) |
| `OPENAI_API_KEY` | `""` | Optional OpenAI key (used strictly for itinerary phrasing; never for numeric crowd scoring) |
| `ADMIN_SECRET_KEY` | `""` | Optional secret for administrative endpoints (open when blank for demo evaluation) |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed frontend origins |

---

## 📋 Comprehensive Milestone Verification Status

- [x] **M1 Tourist Experience**: Deterministic 6-factor crowd scoring, 0–100 gauge, natural language explainability.
- [x] **M2A Smart Date Advisor**: Temporal flow distribution, off-peak date alternatives, 7-day crowd forecasts.
- [x] **M2B Adaptive AI Travel Intelligence**: Service-layer abstracted multi-day itineraries with crowd avoidance.
- [x] **M3 Rural Tourism Ecosystem**: Homestay listings with verified Gram Panchayat badges and local revenue split.
- [x] **M4 Tourism Data Intelligence**: Regional administrative command center with flow monitoring.
- [x] **M5 Production Data + Trust Layer**: Strict provenance labeling, zero unverified claims.
- [x] **M6A/B ML Benchmark Pipeline**: Chronologically evaluated supervised XGBoost model for predictive benchmarking.
- [x] **M7A First-Party Telemetry**: In-platform search, view, and alternative acceptance event stream.
- [x] **M7B Event & Holiday Intelligence**: Regional festival and gazetted holiday impact scoring.
- [x] **M7C Dynamic Live Conditions**: Live weather, road corridors, and dynamic operational pressure recalculation.
- [x] **M7D Capacity-Aware Flow Management**: Circuit network graph, carrying capacity health, and absorption simulation.
- [x] **M7E Verified Booking State Machine**: QR digital travel passes and booking conversion lifecycle.
- [x] **M7F Safety, SOS & Emergency Operations**: Distress beacon broadcast, volunteer responder coordination, and national emergency directory.
- [x] **M7G Panchayat, Host & Rural Economy**: Local host onboarding, 90-5-5 revenue split, and panchayat ledger.
- [x] **M7H Production Hardening**: Live OpenWeather integration, OpenAI itinerary adapter, rate limiting, and secret sanitization.

**Automated Test Baseline**: **236 passed, 0 failed, 0 regressions** across unit and integration test suites.
