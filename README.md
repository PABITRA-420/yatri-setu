# 🏔️ Yatri Setu (यात्री सेतु)
### Hyperlocal & Rural Tourism Platform with Active Crowd Management & Traveler Safety
**Smart India Hackathon 2026** • Core Milestone: Complete Tourist Experience

---

## 🌟 Core Differentiator
Most commercial travel websites operate as passive booking engines, exacerbating overtourism by routing thousands of travelers into already saturated hotspots.

**Yatri Setu actively manages tourist flow.** When fragile mountain destinations (such as Darjeeling during peak autumn sunrise/tea season) reach severe congestion, Yatri Setu:
1. **Computes a deterministic crowd index (0–100)** and classifies it as **LOW / MEDIUM / HIGH / VERY HIGH**.
2. **Generates natural language explainability** for why the score is high (e.g. 91% hotel saturation, Hill Cart Road bottlenecks, Tiger Hill observation deck choke points).
3. **Recommends high-similarity rural alternatives** (e.g. Kalimpong, Lava, Lolegaon, Rishop, Mirik).
4. **Calculates similarity score, distance, and cost savings** (e.g. Kalimpong: 87% similarity, 42% cost savings, 50 km away).
5. **Connects travelers to verified rural panchayat homestays** where 10% of spend supports local village development funds.
6. **Protects travelers with built-in Emergency SOS**, transmitting real-time GPS telemetry to the nearest police, hospital, and local *Yatri Mitra* volunteer responders.

---

## 🗂️ Architecture & Folder Structure

```
yatri-setu/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI entry point with CORS & health check
│   │   ├── core/
│   │   │   ├── config.py               # App configuration & settings
│   │   ├── data/
│   │   │   └── seed_data.py            # Curated seed data for 6 Himalayan destinations
│   │   ├── models/
│   │   │   ├── destination.py          # Destination & Attraction schemas
│   │   │   ├── crowd.py                # Multi-factor crowd metrics & alternatives schemas
│   │   │   ├── itinerary.py            # Activity slot & multi-day itinerary schemas
│   │   │   ├── homestay.py             # Rural homestay, booking & trip schemas
│   │   │   └── safety.py               # Emergency SOS & responder schemas
│   │   ├── services/
│   │   │   ├── crowd_engine.py         # Deterministic 6-factor crowd calculation
│   │   │   ├── alternative_engine.py   # Multi-attribute similarity ranking
│   │   │   ├── itinerary_service.py    # Service-layer abstracted itinerary generation
│   │   │   └── safety_service.py       # Distress beacon & responder dispatch simulator
│   │   └── api/
│   │       └── v1/
│   │           ├── api.py              # Consolidated API v1 router
│   │           ├── destinations.py     # /api/destinations endpoints
│   │           ├── itinerary.py        # /api/itinerary/generate endpoint
│   │           ├── homestays.py        # /api/homestays, /api/bookings, /api/trips endpoints
│   │           └── safety.py           # /api/safety/sos endpoint
│   ├── tests/
│   │   ├── test_crowd_engine.py        # Weights, threshold & similarity unit tests
│   │   └── test_api_endpoints.py       # FastAPI HTTP endpoint integration tests
│   ├── pytest.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx              # Root layout with responsive Navbar & Footer
│   │   │   ├── globals.css             # Tailwind CSS design system tokens
│   │   │   ├── page.tsx                # 1. Landing page with smart search & ticker
│   │   │   ├── dashboard/page.tsx      # 2. Tourist dashboard
│   │   │   ├── destinations/
│   │   │   │   ├── page.tsx            # 3. Destination search & crowd level filter
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx        # 4. Destination details & attractions
│   │   │   │       ├── crowd/page.tsx  # 5. Crowd intelligence panel
│   │   │   │       └── alternatives/page.tsx # 6. Alternate destination advisor
│   │   │   ├── itinerary/page.tsx      # 7 & 8. AI itinerary planner & results timeline
│   │   │   ├── homestays/page.tsx      # 9. Verified rural homestays listing
│   │   │   ├── booking/confirmation/page.tsx # 10. Booking confirmation & QR pass
│   │   │   ├── trips/[id]/page.tsx     # 11. Active trip companion dashboard
│   │   │   └── safety/sos/page.tsx     # 12. SOS safety screen & live responder beacon
│   │   ├── components/
│   │   │   ├── Navbar.tsx              # Sticky header with quick SOS trigger
│   │   │   ├── Footer.tsx              # SIH 2026 footer & national helplines
│   │   │   ├── CrowdGauge.tsx          # Circular 0-100 crowd meter with status dot
│   │   │   ├── CrowdFactorBreakdown.tsx# Progress bars for the 6 weighted factors
│   │   │   ├── AlternativeCard.tsx     # Similarity %, cost savings & explainability
│   │   │   ├── DestinationCard.tsx     # Destination card with crowd status
│   │   │   ├── HomestayCard.tsx        # Panchayat stay card with 10% community fund
│   │   │   └── ItineraryTimeline.tsx   # Interactive day-by-day activity slots
│   │   ├── lib/
│   │   │   ├── api.ts                  # Client connecting to FastAPI (with offline fallback)
│   │   │   └── utils.ts                # Styling utilities & formatINR
│   │   └── types/
│   │       └── index.ts                # TypeScript interfaces matching backend models
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

---

## ⚙️ Deterministic Crowd Score Formula

```text
crowd_score =
  35% × historical_footfall +
  25% × booking_density +
  15% × seasonality +
  10% × holiday_factor +
  10% × weather_event_factor +
   5% × traffic_factor
```

### Classification Thresholds:
- **0 – 25**: `LOW` (Emerald Green) — Pristine tranquility, e.g., Rishop (15), Lolegaon (18), Lava (24).
- **26 – 50**: `MEDIUM` (Amber) — Balanced footfall, e.g., Kalimpong (42), Mirik (38).
- **51 – 75**: `HIGH` (Orange) — Elevated density, viewpoint lines.
- **76 – 100**: `VERY HIGH` (Rose Red) — Critical congestion alert, e.g., Darjeeling (88).

---

## 🧭 Core Demo Flow for SIH 2026 Judges

1. **Landing Page (`/`)**:
   - Inspect the regional live crowd ticker.
   - Click **"Launch Darjeeling Demo"** or search "Darjeeling".
2. **Crowd Intelligence Panel (`/destinations/darjeeling/crowd`)**:
   - View the circular gauge showing **VERY HIGH 88/100**.
   - Read the explainability bullet points ("Why is it crowded?").
   - Review the 6 factor breakdown bars.
   - Click **"View Recommended Alternatives"**.
3. **Alternate Destination Advisor (`/destinations/darjeeling/alternatives`)**:
   - Note **Kalimpong** ranked as top alternative with **87% Similarity**, **42/100 (Medium Crowd)**, and **42% Cost Savings**.
   - Click **"Choose Kalimpong & Generate Itinerary"**.
4. **AI Itinerary Planner (`/itinerary?destination=kalimpong`)**:
   - Inspect the crowd-avoidance rating: *"91% Overcrowding Avoided"*.
   - Browse Day 1, Day 2, and Day 3 timeline tabs with morning/afternoon/evening slots.
   - Click **"Select Verified Homestay"**.
5. **Homestays (`/homestays?destination_id=kalimpong`)**:
   - Inspect *Pineview Orchid Retreat & Homestay* (Panchayat Verified, 10% Village Fund).
   - Click **"Reserve Stay"**.
6. **Booking Confirmation (`/booking/confirmation`)**:
   - Confirm booking to generate the **Digital Travel Pass QR**.
   - Click **"Go to Active Trip Dashboard"**.
7. **Active Trip Dashboard (`/trips/YS-BK-...`)**:
   - Review packing checklist, weather alert, and digital pass.
   - Click **"TRIGGER SOS RESCUE BEACON"**.
8. **SOS Safety Screen (`/safety/sos`)**:
   - Click the large red **"HOLD SOS"** button.
   - Watch the screen activate into a live pulsing emergency broadcast with GPS coordinates (`27.0667° N, 88.4667° E`) and 3 dispatched emergency responders (Police Station, District Hospital, and Yatri Mitra Unit 4).

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ (Tested on v22.17.0)
- npm 9+

### 1. Start the FastAPI Backend
```bash
# In the project root directory:
pip install -r backend/requirements.txt

# Run backend unit & integration tests:
$env:PYTHONPATH="backend"; python -m pytest backend/tests

# Launch the FastAPI dev server (port 8000):
$env:PYTHONPATH="backend"; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Health: `http://127.0.0.1:8000/health`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

### 2. Start the Next.js Frontend
```bash
# In a new terminal, navigate to the frontend directory:
cd frontend

# Install dependencies (already installed):
npm install

# Start development server:
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🔐 Environment Variables

| Variable | Location | Default | Description |
| :--- | :--- | :--- | :--- |
| `ENV` | `backend` | `development` | Runtime environment mode |
| `DATABASE_URL` | `backend` | `postgresql://user:pass@localhost:5432/yatrisetu` | Future PostgreSQL/PostGIS database URL |
| `NEXT_PUBLIC_API_URL` | `frontend` | `http://localhost:8000/api` | Base URL for FastAPI backend |

---

## 📋 Implemented Features Catalog

- [x] **Smart Crowd & Alternate-Destination Advisor**: Multi-factor scoring with natural language explainability.
- [x] **Regional Footfall Ticker**: Live status for 6 North Bengal foothill & hill station locations.
- [x] **Cosine Attribute Similarity Engine**: Matches alternative destinations by nature, culture, activities, and distance.
- [x] **AI Itinerary Planner**: Service-layer abstracted multi-day itineraries with time slots and budget estimates.
- [x] **Verified Rural Homestays**: Direct community stay booking simulation with panchayat badge and 10% village fund contribution.
- [x] **Digital Travel Pass**: Offline-capable travel QR pass simulation.
- [x] **Active Trip Companion**: Packing checklist, weather advisories, and host contacts.
- [x] **Traveler Safety & Emergency SOS**: Telemetry broadcast simulation, siren toggle, and responder dispatch.
- [x] **Responsive Mobile-First Travel-Tech Design**: Terracotta, emerald, and warm saffron Indian travel-tech aesthetic.
- [x] **Automated Test Suite**: 12 backend unit and API tests with 100% passing rate.

---

## 🔮 Future ML & PostGIS Roadmap
1. **Machine Learning Forecasting**: Replace deterministic weights with a trained gradient boosted model (XGBoost/LightGBM) using historical weather archives, holiday calendars, and mobile cellular tower density feeds.
2. **PostgreSQL / PostGIS Spatial Queries**: Compute precise geodesic isochrones and road topology elevation contours.
3. **LLM Integration**: Plug Anthropic Claude / OpenAI APIs into the existing `itinerary_service.py` interface for open-ended conversational trip planning.
4. **Host & Panchayat Portal**: A dedicated administrative dashboard for village panchayat nodal officers to approve new homestays and receive live tourist density heatmaps.
