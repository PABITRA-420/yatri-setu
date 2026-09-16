"""
Destination Network Service for Yatri Setu (Milestone 7D).
Evaluates network reachability, route feasibility, and corridor health.
"""

from typing import List, Optional
from app.services.network.schemas import DestinationNetworkEdge
from app.services.network.repository import destination_network_repository, DestinationNetworkRepository


class DestinationNetworkService:
    def __init__(self, repository: Optional[DestinationNetworkRepository] = None):
        self._repo = repository or destination_network_repository

    def get_candidate_destinations(self, source_id: str) -> List[str]:
        """Returns reachable target destination IDs for a given source."""
        edges = self._repo.get_outbound_edges(source_id, active_only=True)
        return [e.target_destination_id for e in edges]

    def get_edge(self, source_id: str, target_id: str) -> Optional[DestinationNetworkEdge]:
        """Returns specific edge between source and target."""
        return self._repo.get_edge(source_id, target_id)

    def get_outbound_edges(self, source_id: str) -> List[DestinationNetworkEdge]:
        """Returns all active outbound edges for source destination."""
        return self._repo.get_outbound_edges(source_id, active_only=True)

    def is_route_feasible(self, source_id: str, target_id: str) -> bool:
        """
        Checks whether transfer feasibility between source and target is valid.
        Excludes inactive edges or DISRUPTED feasibility.
        """
        edge = self.get_edge(source_id, target_id)
        if not edge or not edge.active:
            return False
        return edge.transfer_feasibility != "DISRUPTED"

    def list_all_edges(self) -> List[DestinationNetworkEdge]:
        return self._repo.list_all_edges()


destination_network_service = DestinationNetworkService()
