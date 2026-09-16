"""
Base Provider Interfaces for Safety & Emergency Operations (Milestone 7F).
Defines abstract contracts for incident broadcasting and multi-channel notifications.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseSafetyProvider(ABC):
    """Abstract interface for emergency incident dispatch and responder coordination."""

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if provider is healthy and configured."""
        pass

    @abstractmethod
    def dispatch_sos(self, incident_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches distress alert and returns responder details & dispatch status."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns identifier of provider (e.g. 'INTERNAL_NETWORK', 'DEMO', 'REAL_EXTERNAL')."""
        pass


class BaseNotificationProvider(ABC):
    """Abstract interface for operator & traveler notification delivery."""

    @abstractmethod
    def send_notification(
        self,
        incident_id: str,
        recipient_type: str,
        channel: str,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Dispatches notification and returns delivery receipt."""
        pass
