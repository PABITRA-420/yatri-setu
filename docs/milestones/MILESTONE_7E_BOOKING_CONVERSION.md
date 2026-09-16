# Milestone 7E: Real Booking / Availability + First-Party Conversion Intelligence

## Executive Summary
Milestone 7E promotes Yatri Setu's accommodation reservation and telemetry architecture to **Real Booking / Availability and First-Party Conversion Intelligence**. Prior to Milestone 7E, flow management relied on configured redirect acceptance rates (`REDIRECTION_ACCEPTANCE_RATE = 0.15`) and booking simulations.

Milestone 7E establishes:
1. **A deterministic booking state machine** with explicit states, transitions, concurrency locks, and double-booking prevention.
2. **Date-aware accommodation availability ledger** supporting granular room-level reservation and atomic release.
3. **Comprehensive first-party telemetry events** covering the full end-to-end tourist flow (view $\rightarrow$ select dates $\rightarrow$ review alternatives $\rightarrow$ check availability $\rightarrow$ initiate booking $\rightarrow$ confirm booking $\rightarrow$ start trip).
4. **Outbound booking referral click tracking** distinct from confirmed platform bookings, ensuring truth-in-reporting.
5. **Empirical conversion funnel and observed acceptance rates** that transition gracefully from configured conservative defaults ($15\%$) to observed reality once statistical sample thresholds ($N \ge 20$) are met.

---

## 1. Booking State Machine Architecture

### State Machine Lifecycle
```
[INITIATED]
    │
    ▼
[AVAILABILITY_CHECKED]
    │
    ├── (Room Sold Out / Locked) ───────────► [FAILED]
    ▼
[PENDING_CONFIRMATION]
    │
    ├── (Host/Panchayat Approval / Payment) ─► [CONFIRMED]
    ├── (Timeout / Unconfirmed) ─────────────► [EXPIRED]
    └── (Traveler Cancellation) ─────────────► [CANCELLED]
```

### State Definitions
- **`INITIATED`**: Traveler begins checkout process for a specific homestay and date range.
- **`AVAILABILITY_CHECKED`**: Real inventory ledger verified for all requested dates.
- **`PENDING_CONFIRMATION`**: Room units held in reservation lock pending host/payment confirmation.
- **`CONFIRMED`**: Atomic room reservation committed, digital travel pass QR issued, and panchayat nodal desk notified.
- **`FAILED`**: Explicit termination with deterministic `failure_reason` (`SOLD_OUT`, `ROOM_LOCKED`, `INVALID_HOMESTAY`, `INVALID_DATES`, `PAYMENT_FAILED`).
- **`CANCELLED`**: Traveler or host cancels booking; room units atomically returned to available pool.
- **`EXPIRED`**: Booking hold window lapsed before confirmation; units released.

### Transition Guardrails & Concurrency
- Transitions are deterministic and validated against allowed transitions (`BookingLifecycleService._validate_transition`).
- Concurrent booking requests for the final available room are guarded by thread locks (`threading.Lock`).
- The losing concurrent thread fails immediately with `SOLD_OUT` (HTTP 409) rather than creating double-bookings or phantom reservations.
- Cancellation triggers atomic inventory replenishment via `availability_service.release_units()`.

---

## 2. Date-Aware Accommodation Availability

### Granular Inventory Model
- **`HomestayAvailabilitySnapshot`**:
  - `homestay_id`, `homestay_name`, `destination_id`, `destination_name`
  - `date`: Target calendar date (`YYYY-MM-DD`)
  - `total_units`: Configured room count for listing
  - `reserved_units`: Currently locked or confirmed reservations for date
  - `available_units`: $\max(0, \text{total\_units} - \text{reserved\_units})$
  - `status`: `AVAILABLE` ($>1$ unit), `FEW_LEFT` ($1$ unit), `SOLD_OUT` ($0$ units)
  - `is_bookable`: Boolean flag ($available > 0$)
  - `data_quality`: `HIGH` (verified homestay listing)

- **`DestinationAvailabilitySnapshot`**:
  - Aggregates all homestay snapshots for the destination on a given date.
  - Reports `total_homestays`, `total_units`, `reserved_units`, `available_units`, `occupancy_rate`, and destination-wide `status`.

---

## 3. First-Party Telemetry & Funnel Metrics

### Extended Demand Event Types
Milestone 7E expands `DemandEventType` to instrument the complete traveler journey:
1. `SEARCH`: Origin inquiry or circuit search.
2. `DESTINATION_VIEW`: Detailed destination inspection.
3. `DATE_SELECTED`: Arrival/departure date specification.
4. `ALTERNATIVE_VIEWED`: Dispersal recommendation presented to user.
5. `ALTERNATIVE_ACCEPTED`: User explicitly selects recommended alternative destination/date.
6. `AVAILABILITY_CHECKED`: Inventory query for target dates.
7. `BOOKING_INITIATED`: Reservation flow started.
8. `BOOKING_CONFIRMED`: Verified booking finalized.
9. `BOOKING_FAILED`: Reservation rejected (e.g. sold out).
10. `BOOKING_CANCELLED`: Confirmed stay cancelled.
11. `OUTBOUND_BOOKING_CLICK`: External referral to third-party hotel or partner OTA.
12. `TRIP_STARTED`: Tourist arrived / active travel pass validated.

### Non-PII Telemetry Guarantees
- Event metadata contains only operational signals (destination, session ID, room count, nights).
- Passwords, full credit card numbers, and PII are strictly excluded from telemetry payloads.

---

## 4. Conversion Funnel & Acceptance Rate Integration

### Acceptance Rate Modes
To eliminate artificial precision when data is sparse, the system utilizes a multi-mode acceptance rate calculator:
- **`CONFIGURED` / `INSUFFICIENT_DATA`**: Sample size $N < 20$. The system preserves the verified conservative fallback `REDIRECTION_ACCEPTANCE_RATE = 0.15` (15%) to prevent volatile, unrepresentative flow swings.
- **`OBSERVED`**: Sample size $N \ge 20$. The system calculates empirical acceptance:
  $$\text{Observed Acceptance Rate} = \frac{\text{ALTERNATIVE\_ACCEPTED}}{\text{ALTERNATIVE\_VIEWED}}$$
- **Effective Flow Rate**: When in `OBSERVED` mode, `effective_acceptance_rate` feeds dynamically into `simulateFlow` and capacity dispersal calculations.

### Outbound Booking Referral Distinction
Outbound clicks to partner OTAs (e.g., MakeMyTrip, Booking.com) are tracked distinctly under `OUTBOUND_BOOKING_CLICK`:
- The system logs the partner ID, referral URL, and timestamp.
- Outbound clicks are **never reported as confirmed bookings** or counted toward local village community funds until verified by partner webhooks.

---

## 5. API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/bookings` | Create & process booking via deterministic state machine |
| `GET` | `/api/bookings/{id}` | Get lifecycle state and transition audit history |
| `POST` | `/api/bookings/{id}/confirm` | Confirm booking in `PENDING_CONFIRMATION` |
| `POST` | `/api/bookings/{id}/cancel` | Cancel booking & atomically release units to ledger |
| `GET` | `/api/homestays/{id}/availability` | Date-aware availability snapshot for homestay |
| `GET` | `/api/destinations/{id}/availability` | Date-aware destination capacity & occupancy snapshot |
| `GET` | `/api/admin/conversion/summary` | Complete conversion funnel, acceptance modes, destination metrics |
| `GET` | `/api/admin/conversion/funnel` | Stage-by-stage counts and drop-off rates |
| `POST` | `/api/conversion/events` | Record first-party conversion telemetry event |

---

## 6. Verification & Test Coverage

### Automated Backend Tests
- `backend/tests/test_milestone7e_booking_conversion.py`:
  - `test_booking_lifecycle_state_machine`: Verifies `INITIATED` $\rightarrow$ `AVAILABILITY_CHECKED` $\rightarrow$ `PENDING_CONFIRMATION` $\rightarrow$ `CONFIRMED` $\rightarrow$ `CANCELLED`.
  - `test_invalid_state_transition_rejected`: Ensures illegal jumps (e.g. `CONFIRMED` $\rightarrow$ `INITIATED`) raise `ValueError`.
  - `test_concurrency_and_double_booking_protection`: Simulates concurrent threads contending for the last remaining unit; exactly 1 succeeds and 1 fails with `SOLD_OUT`.
  - `test_date_aware_homestay_availability`: Validates date-specific unit subtraction and restoration.
  - `test_destination_availability_snapshot`: Validates multi-homestay rollup and occupancy calculation.
  - `test_booking_failure_sold_out`: Verifies HTTP 409 and failure reason logging.
  - `test_outbound_click_tracking`: Validates isolation between outbound referral clicks and platform bookings.
  - `test_conversion_funnel_summary`: Verifies funnel stages, drop-off denominators, and observed vs configured modes.
  - `test_telemetry_event_recording_no_pii`: Validates non-PII compliance and metadata storage.
  - `test_get_booking_details_endpoint`: Tests `/api/bookings/{id}` state querying.
  - `test_confirm_booking_endpoint`: Tests manual confirmation flow.
  - `test_cancel_booking_endpoint`: Tests cancellation and inventory restoration.

### Baseline Status
- **Backend Tests**: 194 passing, 0 failing (100% green).
- **TypeScript**: 0 compiler errors (`npx tsc --noEmit`).
- **Next.js Production Build**: 21/21 routes generated and optimized successfully.
