"""
Destination Network Repository for Yatri Setu (Milestone 7D).
Maintains bidirectional circuit network edges across Darjeeling, Kalimpong, Lava, Lolegaon, Rishop, and Mirik.
"""

from typing import Dict, List, Optional
from app.services.network.schemas import DestinationNetworkEdge


# Curated network topology based on Himalayan mountain road arteries
INITIAL_NETWORK_EDGES: List[DestinationNetworkEdge] = [
    # Darjeeling <-> Kalimpong
    DestinationNetworkEdge(
        source_destination_id="darjeeling",
        target_destination_id="kalimpong",
        route_distance_km=50.0,
        typical_travel_time_min=110,
        alternative_type="NEIGHBORING_CIRCUIT",
        corridor_ids=["rt-darj-nh55", "rt-kalim-nh10"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),
    DestinationNetworkEdge(
        source_destination_id="kalimpong",
        target_destination_id="darjeeling",
        route_distance_km=50.0,
        typical_travel_time_min=110,
        alternative_type="NEIGHBORING_CIRCUIT",
        corridor_ids=["rt-kalim-nh10", "rt-darj-nh55"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),

    # Darjeeling <-> Mirik
    DestinationNetworkEdge(
        source_destination_id="darjeeling",
        target_destination_id="mirik",
        route_distance_km=49.0,
        typical_travel_time_min=95,
        alternative_type="TRANQUIL_RETREAT",
        corridor_ids=["rt-darj-pankhabari", "rt-mirik-sukhiapokhri"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),
    DestinationNetworkEdge(
        source_destination_id="mirik",
        target_destination_id="darjeeling",
        route_distance_km=49.0,
        typical_travel_time_min=95,
        alternative_type="NEIGHBORING_CIRCUIT",
        corridor_ids=["rt-mirik-sukhiapokhri", "rt-darj-pankhabari"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),

    # Darjeeling <-> Lava
    DestinationNetworkEdge(
        source_destination_id="darjeeling",
        target_destination_id="lava",
        route_distance_km=78.0,
        typical_travel_time_min=160,
        alternative_type="NATURE_SANCTUARY",
        corridor_ids=["rt-darj-nh55", "rt-kalim-nh10", "rt-lava-algarah"],
        seasonality="MONSOON_CAUTION",
        transfer_feasibility="MODERATE",
        active=True
    ),
    DestinationNetworkEdge(
        source_destination_id="lava",
        target_destination_id="darjeeling",
        route_distance_km=78.0,
        typical_travel_time_min=160,
        alternative_type="NEIGHBORING_CIRCUIT",
        corridor_ids=["rt-lava-algarah", "rt-kalim-nh10", "rt-darj-nh55"],
        seasonality="MONSOON_CAUTION",
        transfer_feasibility="MODERATE",
        active=True
    ),

    # Kalimpong <-> Lava
    DestinationNetworkEdge(
        source_destination_id="kalimpong",
        target_destination_id="lava",
        route_distance_km=34.0,
        typical_travel_time_min=75,
        alternative_type="NATURE_SANCTUARY",
        corridor_ids=["rt-kalim-rishi", "rt-lava-algarah"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),
    DestinationNetworkEdge(
        source_destination_id="lava",
        target_destination_id="kalimpong",
        route_distance_km=34.0,
        typical_travel_time_min=75,
        alternative_type="CULTURAL_ALTERNATIVE",
        corridor_ids=["rt-lava-algarah", "rt-kalim-rishi"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),

    # Kalimpong <-> Lolegaon
    DestinationNetworkEdge(
        source_destination_id="kalimpong",
        target_destination_id="lolegaon",
        route_distance_km=52.0,
        typical_travel_time_min=110,
        alternative_type="TRANQUIL_RETREAT",
        corridor_ids=["rt-kalim-rishi", "rt-lole-forest"],
        seasonality="MONSOON_CAUTION",
        transfer_feasibility="MODERATE",
        active=True
    ),
    DestinationNetworkEdge(
        source_destination_id="lolegaon",
        target_destination_id="kalimpong",
        route_distance_km=52.0,
        typical_travel_time_min=110,
        alternative_type="CULTURAL_ALTERNATIVE",
        corridor_ids=["rt-lole-forest", "rt-kalim-rishi"],
        seasonality="MONSOON_CAUTION",
        transfer_feasibility="MODERATE",
        active=True
    ),

    # Kalimpong <-> Rishop
    DestinationNetworkEdge(
        source_destination_id="kalimpong",
        target_destination_id="rishop",
        route_distance_km=28.0,
        typical_travel_time_min=65,
        alternative_type="TRANQUIL_RETREAT",
        corridor_ids=["rt-kalim-rishi", "rt-rishop-trail"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),
    DestinationNetworkEdge(
        source_destination_id="rishop",
        target_destination_id="kalimpong",
        route_distance_km=28.0,
        typical_travel_time_min=65,
        alternative_type="CULTURAL_ALTERNATIVE",
        corridor_ids=["rt-rishop-trail", "rt-kalim-rishi"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),

    # Lava <-> Lolegaon
    DestinationNetworkEdge(
        source_destination_id="lava",
        target_destination_id="lolegaon",
        route_distance_km=24.0,
        typical_travel_time_min=55,
        alternative_type="TRANQUIL_RETREAT",
        corridor_ids=["rt-lava-algarah", "rt-lole-forest"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),
    DestinationNetworkEdge(
        source_destination_id="lolegaon",
        target_destination_id="lava",
        route_distance_km=24.0,
        typical_travel_time_min=55,
        alternative_type="NATURE_SANCTUARY",
        corridor_ids=["rt-lole-forest", "rt-lava-algarah"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),

    # Lava <-> Rishop
    DestinationNetworkEdge(
        source_destination_id="lava",
        target_destination_id="rishop",
        route_distance_km=11.0,
        typical_travel_time_min=30,
        alternative_type="TRANQUIL_RETREAT",
        corridor_ids=["rt-lava-algarah", "rt-rishop-trail"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),
    DestinationNetworkEdge(
        source_destination_id="rishop",
        target_destination_id="lava",
        route_distance_km=11.0,
        typical_travel_time_min=30,
        alternative_type="NATURE_SANCTUARY",
        corridor_ids=["rt-rishop-trail", "rt-lava-algarah"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),

    # Lolegaon <-> Rishop
    DestinationNetworkEdge(
        source_destination_id="lolegaon",
        target_destination_id="rishop",
        route_distance_km=30.0,
        typical_travel_time_min=70,
        alternative_type="TRANQUIL_RETREAT",
        corridor_ids=["rt-lole-forest", "rt-rishop-trail"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    ),
    DestinationNetworkEdge(
        source_destination_id="rishop",
        target_destination_id="lolegaon",
        route_distance_km=30.0,
        typical_travel_time_min=70,
        alternative_type="TRANQUIL_RETREAT",
        corridor_ids=["rt-rishop-trail", "rt-lole-forest"],
        seasonality="ALL_SEASON",
        transfer_feasibility="HIGH",
        active=True
    )
]


class DestinationNetworkRepository:
    def __init__(self):
        self._edges: Dict[str, List[DestinationNetworkEdge]] = {}
        self._edge_lookup: Dict[str, DestinationNetworkEdge] = {}
        for edge in INITIAL_NETWORK_EDGES:
            self.add_edge(edge)

    def add_edge(self, edge: DestinationNetworkEdge):
        s_id = edge.source_destination_id.lower().strip()
        t_id = edge.target_destination_id.lower().strip()
        key = f"{s_id}->{t_id}"
        self._edge_lookup[key] = edge
        if s_id not in self._edges:
            self._edges[s_id] = []
        # Update or append
        existing = [e for e in self._edges[s_id] if e.target_destination_id == t_id]
        if existing:
            self._edges[s_id].remove(existing[0])
        self._edges[s_id].append(edge)

    def get_outbound_edges(self, source_id: str, active_only: bool = True) -> List[DestinationNetworkEdge]:
        s_id = source_id.lower().strip()
        edges = self._edges.get(s_id, [])
        if active_only:
            return [e for e in edges if e.active]
        return list(edges)

    def get_edge(self, source_id: str, target_id: str) -> Optional[DestinationNetworkEdge]:
        s_id = source_id.lower().strip()
        t_id = target_id.lower().strip()
        return self._edge_lookup.get(f"{s_id}->{t_id}")

    def list_all_edges(self) -> List[DestinationNetworkEdge]:
        return list(self._edge_lookup.values())


destination_network_repository = DestinationNetworkRepository()
