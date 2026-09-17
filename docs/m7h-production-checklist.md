# Milestone 7H: Production Hardening & Deployment Checklist

This document provides the authoritative deployment and operations guide for **Yatri Setu** (Smart India Hackathon 2026), covering backend hosting on **Render**, frontend hosting on **Vercel**, **PostgreSQL** database connectivity, provider fallbacks, secret hygiene, and monitoring.

---

## 1. Cloud Architecture Overview

$$\begin{matrix}
\textbf{Vercel (Edge Frontend)} & \xrightarrow[\text{JSON via HTTPS}]{\text{NEXT\_PUBLIC\_API\_URL}} & \textbf{Render (FastAPI Web Service)} \\
\text{Next.js 16 (App Router)} & & \text{Uvicorn + Python 3.11} \\
& & \big\downarrow \\
& & \textbf{PostgreSQL (Managed DB)} \\
& & \text{Neon / Supabase / Render Postgres}
\end{matrix}$$

---

## 2. Environment Variables Checklist

### A. Backend Web Service (Render)

Configure these in **Render Dashboard &rarr; Environment**:

| Variable Name | Required? | Example Value | Description |
| :--- | :---: | :--- | :--- |
| `ENVIRONMENT` | **Yes** | `production` | Declares runtime environment |
| `DATABASE_URL` | **Yes** | `postgresql://user:pass@ep-xyz.region.aws.neon.tech/yatri_setu` | Production PostgreSQL connection string |
| `CORS_ORIGINS` | **Yes** | `https://yatri-setu.vercel.app,http://localhost:3000` | Comma-separated allowed frontend origins (no wildcards) |
| `WEATHER_PROVIDER` | Optional | `openweather` (or `demo`) | Active weather adapter (`openweather` for live data) |
| `WEATHER_API_KEY` | Optional | `your_openweathermap_api_key` | OpenWeather API key (backend only; never exposed to client) |
| `AI_PROVIDER` | Optional | `gemini` (or `groq`, `mock`) | Primary AI itinerary provider (`gemini` by default) |
| `GEMINI_API_KEY` | Optional | `AIzaSy...` | Google Gemini API key for primary AI itinerary generation |
| `GEMINI_MODEL` | Optional | `gemini-3.6-flash` | Gemini model name (default: `gemini-3.6-flash`) |
| `AI_FALLBACK_PROVIDER` | Optional | `groq` | Secondary fallback AI provider (`groq` by default) |
| `GROQ_API_KEY` | Optional | `gsk_...` | Groq API key for secondary fallback AI enrichment |
| `GROQ_MODEL` | Optional | `openai/gpt-oss-120b` | Groq model name (default: `openai/gpt-oss-120b`) |
| `ADMIN_SECRET_KEY` | Optional | `prod_secret_token_123` | Secret required for admin mutations when configured |
| `PRESSURE_REFRESH_INTERVAL_SECONDS`| Optional | `300` | Automated dynamic crowd pressure recalculation cycle (seconds) |
| `RATE_LIMIT_AI_PER_MINUTE` | Optional | `60` | Application-side sliding window rate limit (reduces risk of quota spikes; does not guarantee upstream quota headroom as quotas are account/provider dependent) |
| `RATE_LIMIT_SOS_PER_MINUTE` | Optional | `120` | Sliding window rate limit for emergency distress alerts |

> [!IMPORTANT]
> **Zero-Key Resilient Default**:
> If `WEATHER_API_KEY`, `GEMINI_API_KEY`, or `GROQ_API_KEY` are not configured, Yatri Setu **never crashes**. The system automatically cascades from Gemini &rarr; Groq &rarr; MockAIProvider and OpenWeather &rarr; Demo Simulator with explicit provenance tags (`DEMO MODE — SYNTHETIC DATA`), ensuring uninterrupted judge demonstrations.

### B. Frontend Web App (Vercel)

Configure in **Vercel Project Settings &rarr; Environment Variables**:

| Variable Name | Required? | Example Value | Description |
| :--- | :---: | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | **Yes** | `https://yatri-setu-api.onrender.com/api` | Base URL pointing to the Render backend API |

---

## 3. PostgreSQL Database Configuration

1. **Automatic URL Normalization**:
   - Cloud providers (such as Render or Heroku) supply connection strings starting with `postgres://`.
   - SQLAlchemy 2.0 requires `postgresql://`.
   - Yatri Setu automatically normalizes `postgres://` to `postgresql://` at runtime in `backend/app/core/config.py`.
2. **Connection Pooling & Pre-Ping**:
   - `pool_pre_ping=True` is enabled in `backend/app/core/database.py` to prevent stale connection errors across cloud idle timeouts.
3. **Graceful Degradation**:
   - If PostgreSQL is temporarily unreachable at startup, `init_db()` logs a warning and the application continues serving cached/in-memory data with health status `degraded` instead of crashing.

---

## 4. Map & Route Provider Policy

> [!NOTE]
> **No External MAPS_API_KEY Required**:
> - Yatri Setu uses a high-precision, curated topological route model of the Darjeeling-Kalimpong Himalayan circuit (`backend/app/services/route_service.py`) and bespoke SVG/canvas maps on the frontend.
> - No external Google Maps or Mapbox API keys are required, eliminating external latency, unexpected billing, and network fragility.

---

## 5. Security & Secret Hygiene Rules

1. **Strict Backend-Only Secrets**:
   - `WEATHER_API_KEY` and `OPENAI_API_KEY` are never bundled into frontend JavaScript, never stored in `localStorage`, and never returned in API payloads.
2. **Log Redaction Filter**:
   - `backend/app/core/logging.py` attaches a `SanitizingFilter` that automatically scrubs `sk-...`, `Bearer ...`, passwords, and API tokens from log outputs.
3. **CORS Explicit Origins**:
   - In production, wildcard `*` is prohibited. Set `CORS_ORIGINS` to the exact Vercel deployment URL.
4. **Git Safety**:
   - Real `.env` and `.env.*` files are ignored via `.gitignore`.
   - Only `backend/.env.example` containing placeholders is committed to source control.
5. **Data Minimization & Privacy**:
   - Host and Panchayat dashboards strictly exclude traveler personal phone numbers, emails, emergency contacts, and raw GPS coordinates.

---

## 6. Operational Health Probe (`GET /health`)

Render and monitoring services should point their health checks to:
`GET /health` or `GET /api/health`

### Example Sanitized Health Check Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "database": {
    "status": "connected",
    "dialect": "postgresql",
    "is_sqlite": false
  },
  "providers": {
    "weather": {
      "provider": "openweather",
      "mode": "REAL",
      "available": true,
      "provenance": "REAL — EXTERNAL PROVIDER"
    },
    "ai": {
      "provider": "gemini",
      "model": "gemini-3.6-flash",
      "configured": true,
      "fallback_provider": "groq",
      "fallback_model": "openai/gpt-oss-120b",
      "fallback_configured": true
    },
    "traffic": {
      "provider": "demo",
      "available": true
    }
  },
  "provenance_policy": {
    "zero_key_demo_supported": true,
    "real_data_distinguished": true,
    "pii_protection": "STRICT_ZERO_PII_HOST_PANCHAYAT"
  }
}
```

---

## 7. Provider Failure & Provenance Matrix

| Subsystem | Real Available | Provider Error / Timeout | Missing API Key | Provenance Label |
| :--- | :--- | :--- | :--- | :--- |
| **Weather** | OpenWeather live data | Stale cache (15 min TTL) or Demo simulator | Demo mountain simulator | `REAL — EXTERNAL PROVIDER` (live)<br>`MIXED — STALE TELEMETRY FALLBACK` (stale)<br>`DEMO MODE — SYNTHETIC DATA` (demo) |
| **AI Itinerary** | Google Gemini (`gemini-3.6-flash`) | Groq (`openai/gpt-oss-120b`) fallback &rarr; Mock adaptive engine | Cascades to Groq &rarr; Mock adaptive engine | Content tagged with `ai_provider_used` (`gemini`, `groq_fallback`, or `mock`) |
| **Crowd Pressure** | 6-factor deterministic engine | Deterministic engine | Deterministic engine | `REAL — YATRI SETU NETWORK` |
| **Capacity & Booking**| Single-source `HomestayRepository` | In-memory atomic store | Atomic store | `REAL — YATRI SETU NETWORK` |
| **Safety / SOS** | Yatri Mitra volunteer network | In-memory atomic queue | Local queue | `REAL — YATRI SETU NETWORK` |
