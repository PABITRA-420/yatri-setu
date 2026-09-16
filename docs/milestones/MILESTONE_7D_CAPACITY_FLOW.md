# Milestone 7D: Capacity-Aware Flow Management & Destination Network Intelligence

## Executive Summary
Milestone 7D transforms Yatri Setu from simple crowd-based alternative discovery to **Capacity-Aware Flow Management and Destination Network Intelligence**. The primary mission is to eliminate the classic tourism redirection cascade failure:
$$\text{Origin Congestion} \longrightarrow \text{Unchecked Redirection} \longrightarrow \text{Secondary Destination Saturation}$$

By verifying candidate receiving capacity, corridor accessibility, mountain weather, and projected pressure surge prior to recommendation and planning, Yatri Setu ensures sustainable rural mountain tourism dispersal.

---

## 1. Destination Network Architecture
The destination network represents topological, geographical, and arterial route relationships between destinations in the circuit:
- **Topology**: Models 14+ bidirectional edges across `Darjeeling`, `Kalimpong`, `Lava`, `Lolegaon`, `Rishop`, and `Mirik`.
- **Schema (`DestinationNetworkEdge`)**:
  - `source_destination_id`, `target_destination_id`
  - `route_distance_km` (actual mountain road distance)
  - `typical_travel_time_min` (typical travel duration)
  - `alternative_type` (`NEIGHBORING_CIRCUIT`, `CULTURAL_ALTERNATIVE`, `NATURE_SANCTUARY`, `TRANQUIL_RETREAT`)
  - `corridor_ids` (mapped directly to Milestone 7C traffic corridor monitors)
  - `seasonality` (`ALL_SEASON`, `MONSOON_CAUTION`)
  - `transfer_feasibility` (`HIGH`, `MODERATE`, `LOW`, `DISRUPTED`)
  - `active` (boolean)
  - `source` (`STATIC_CONFIGURATION`)
  - `data_quality` (`HIGH`)
- **Feasibility Filter**: An edge marked as `DISRUPTED` or inactive is excluded from routing candidates.

---

## 2. Capacity Model & Operational Classifications
Accommodation units are standardized across all facilities as **rooms** (`unit_type: "rooms"`):
- `total_units`: Total room capacity in destination.
- `occupied_units`: Currently booked/occupied rooms.
- `available_units`: Ready for guest check-in ($available = total - occupied - reserved$).
- `reserved_units`: Safety margin held for local offline/emergency contingencies.
- `occupancy_rate`: $\frac{occupied}{total}$.
- `estimated_daily_host_capacity`: Total guest headcount capability ($total\_units \times 2$ guests/room).

### Operational Health Thresholds:
- **`HEALTHY`**: Occupancy $< 50\%$
- **`LIMITED`**: Occupancy $50\% - 75\%$
- **`HIGH_UTILIZATION`**: Occupancy $75\% - 90\%$
- **`FULL`**: Occupancy $\ge 90\%$ (Excluded from receiving redirection)
- **`UNKNOWN`**: Incomplete or missing inventory data

---

## 3. Homestay Repository Integration
Rather than maintaining an isolated accommodation database, `DestinationCapacityService` integrates directly with the project's authoritative `HomestayRepository`:
- Queries `homestay_repository._records` for the destination.
- Derives `listed_properties` and `active_properties` ($is\_published = \text{True}$ and $verification\_status \in \{\text{"VERIFIED"}, \text{"PUBLISHED"}\}$).
- Combines verified homestay units with regional baseline hospitality capacity for towns like Darjeeling and Kalimpong.
- Exposes `capacity_data_status`:
  - `AVAILABLE`: Full room-level records and booking ledger.
  - `PARTIAL`: Verified property listings with estimated room allocation.
  - `UNKNOWN`: Missing or unverified properties.

---

## 4. Redirection Absorption Logic (`can_absorb_redirection`)
The function evaluates if a candidate destination can safely absorb an influx of visitors:
```python
can_absorb_redirection(destination_id, expected_redirected_visitors)
```
### Pipeline Checks:
1. **Corridor Access Check**: If main connecting corridor has `access_status == "DISRUPTED"`, returns `eligible = False`.
2. **Severe Weather Check**: If active severe weather warning is present, returns `eligible = False`.
3. **Current Pressure Check**: If current pressure $\ge 80$, returns `eligible = False`.
4. **Capacity Headroom**: Converts visitors into room units ($\lceil visitors / 2 \rceil$). If remaining capacity $< 0$ or status is `FULL`, returns `eligible = False`.
5. **Projected Pressure Feedback Loop**: Simulates pressure surge caused by new occupancy. If projected pressure $\ge 82$, returns `eligible = False` with diagnostic explanation.

---

## 5. Redirection Assumptions & Planning Parameters
- **Parameter**: `REDIRECTION_ACCEPTANCE_RATE` (default `0.15` or 15% in settings).
- **Distinction**:
  - This is an explicit **simulation/planning parameter** unless actual first-party telemetry exists.
  - When tourist-facing alternatives are accepted in the UI, `record_event(alternative_acceptance)` records genuine first-party telemetry.
  - Projected numbers are labeled `SIMULATED — PLANNING SCENARIO` and **never** overwrite live visitor counters.

---

## 6. Flow Simulation & Allocation Planner
The `FlowAllocationPlanner` simulates macro redirection:
- **Input**: Source destination, affected visitors headcount, acceptance rate.
- **Algorithm**:
  - Calculates estimated redirected volume ($affected \times rate$).
  - Queries active outbound network edges for reachable candidates.
  - Evaluates absorption headroom for each candidate.
  - Distributes flow proportionally based on absorbable headroom and current pressure.
  - Labels absorption as `ACCEPTED`, `PARTIAL`, or `REJECTED`.
  - Sets scenario status to `OPTIMAL`, `FLOW_CAPACITY_LIMITED`, or `NO_ELIGIBLE_DESTINATIONS`.

---

## 7. Pressure Feedback Loop
When a hypothetical flow of redirected visitors is assigned to a candidate destination:
- Yatri Setu recalculates **Projected Pressure** dynamically:
  $$\Delta Pressure = \text{round}\left(\frac{\text{Allocated Visitors}}{\text{Daily Host Capacity}} \times 30\right)$$
- If projected pressure surges into critical levels, the planner caps allocation and flags `FLOW_CAPACITY_LIMITED`.

---

## 8. Safety Decoupling
Safety remains strictly independent from crowd pressure:
- A destination can be low crowd but inaccessible (`LOW` crowd + `DISRUPTED` access).
- A destination can be high crowd but completely accessible (`HIGH` crowd + `OPEN` access).
- Disrupted or severe-weather corridors **never** receive redirected flow under any circumstances.

---

## 9. Provenance & Confidence
All network, capacity, and flow outputs include explicit provenance tags:
- Real accommodation and crowd signals: `REAL — YATRI SETU NETWORK`
- Route topology: `STATIC_CONFIGURATION`
- Flow simulations: `SIMULATED — PLANNING SCENARIO`

---

## 10. API Endpoints
- `POST /api/admin/flow/simulate`: Simulates flow distribution across the network.
- `GET /api/admin/capacity/{destination_id}`: Returns accommodation capacity, room counts, and health.
- `GET /api/admin/network/edges`: Returns circuit network graph edges.
- `GET /api/destinations/{id}/alternatives`: Upgraded to return capacity health, available rooms, corridor access, and weather summary per alternative.

---

## 11. Known Limitations & Future Roadmap
- Room-level availability reflects registered properties and baseline capacity; real-time IoT door lock integration or direct PMS API webhooks will further enhance room-level granularity in production.
- Static network relationships represent verified road connections; future road ministry GIS feeds could automatically update road quality.
