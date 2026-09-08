"""
Base AI Provider Interface for Yatri Setu (Smart India Hackathon 2026)
Defines abstract contracts for itinerary generation and adaptive optimization.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.models.itinerary import ItineraryContext, AIItineraryOutput

class BaseAIProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'mock', 'claude', 'openai')."""
        pass

    @abstractmethod
    async def generate_itinerary(self, context: ItineraryContext) -> AIItineraryOutput:
        """Generate a structured, localized itinerary given destination context."""
        pass

    @abstractmethod
    async def optimize_itinerary(
        self,
        context: ItineraryContext,
        current_itinerary: Dict[str, Any],
        instruction: str,
        custom_instruction: Optional[str] = None
    ) -> AIItineraryOutput:
        """Adapt and optimize an existing itinerary according to user directive and conditions."""
        pass
