# Milestone 7 Updates (7A & 7C)

This document summarizes the changes introduced to complete Milestone 7A (Hardening) and Milestone 7C (Weather & Traffic Intelligence).

## Milestone 7A: Telemetry & Hardening

*   **Fixed Search Event Bug**: Addressed an issue where `SearchEvent` could pass a null `destination_id`, ensuring the telemetry accurately handles searches across the Yatri Setu network.
*   **Demand API**: Solidified the implementation of Demand APIs (`GET /api/demand/{destination_id}`, `GET /api/demand/circuit`, `GET /api/admin/demand`) to accurately track destination interest.
*   **Alternative Acceptance**: Improved tracking so that alternative acceptance is *only* recorded when a tourist explicitly accepts or selects an alternative, preventing false positives.
*   **Data Provenance & Trust Layer**: Strictly separated tracking of data sources to ensure synthetic demo data is completely distinct from real Yatri Setu network data.
*   **Homestay Linking**: Hardened the relationship mappings between homestays, tourists, and the Panchayat ecosystem.

## Milestone 7C: Live Weather and Traffic Intelligence

*   **Dynamic Pressure Recalculation**: Implemented `PressureRefreshService` to calculate destination pressure scores dynamically by synthesizing multiple signals (Weather, Traffic, Events, Holidays, Demand, Footfall, Occupancy).
*   **Weather & Traffic Providers**: Added `DemoWeatherProvider` and `DemoTrafficProvider` to supply high-fidelity, Himalayan circuit-specific weather and traffic data.
*   **Causal Explanations**: Introduced "Why Pressure Changed" diagnostics to explain the top drivers (e.g., severe weather, heavy traffic) behind current pressure levels.
*   **Admin Rate Limiting**: Implemented a rate-protected admin endpoint (`POST /api/admin/pressure/refresh`) with a 5-second cooldown to prevent abuse of the refresh functionality.
