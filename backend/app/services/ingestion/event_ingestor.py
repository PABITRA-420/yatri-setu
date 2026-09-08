"""
Event Calendar Ingestor (Milestone 6B).

Ingests cultural and tourism events for Himalayan destinations.

Real Data Assessment:
  - West Bengal Tourism and regional bodies announce events, but these are posted
    as unstructured web pages/PDFs, not machine-readable API endpoints.
  - Eventbrite and similar platforms cover some events but not comprehensive
    for rural Himalayan festivals (Teesta Tea & Tourism Festival, Rimbick Mela, etc.)
  - No legitimate structured API for these local events exists as of 2026.

CONCLUSION:
  Provider mode is MOCK. Events are modeled from known annual festival calendars.
  No fabricated endpoint is used. Clearly labeled as simulated data.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, List

from app.services.ingestion.base_ingestor import (
    BaseIngestor, IngestedObservation, ProviderMode
)

logger = logging.getLogger(__name__)

# Known annual event schedule — SIMULATED from public festival calendars
# NOT a live API; these dates are fixed for demonstration
DESTINATION_ANNUAL_EVENTS = {
    "darjeeling": [
        {"month": 4, "name": "Darjeeling Carnival", "pressure_boost": 25},
        {"month": 5, "name": "Tea Festival", "pressure_boost": 20},
        {"month": 10, "name": "Durga Puja Festival", "pressure_boost": 35},
        {"month": 12, "name": "Christmas & New Year Market", "pressure_boost": 30},
    ],
    "kalimpong": [
        {"month": 4, "name": "Flower Festival", "pressure_boost": 18},
        {"month": 10, "name": "Rimbick Mela", "pressure_boost": 22},
    ],
    "mirik": [
        {"month": 5, "name": "Mirik Lake Festival", "pressure_boost": 15},
        {"month": 10, "name": "Autumn Nature Walk", "pressure_boost": 12},
    ],
    "lava": [
        {"month": 4, "name": "Spring Trekking Season", "pressure_boost": 10},
        {"month": 11, "name": "Birding Festival", "pressure_boost": 12},
    ],
    "lolegaon": [
        {"month": 4, "name": "Canopy Walk Season", "pressure_boost": 8},
        {"month": 11, "name": "Autumn Foliage Season", "pressure_boost": 10},
    ],
    "rishop": [
        {"month": 4, "name": "Rishop Trekking Season", "pressure_boost": 8},
        {"month": 12, "name": "Winter Snowfall Season", "pressure_boost": 15},
    ],
}


class EventIngestor(BaseIngestor):
    """
    Simulates event calendar pressure signal for Himalayan destinations.

    MOCK-only: No live event calendar API exists for these micro-destinations.
    Modeled from publicly announced annual Himalayan tourism festival calendars.
    """

    @property
    def source_label(self) -> str:
        return "Mock Event Calendar (WBTDC Festival Schedule Analog)"

    @property
    def signal_name(self) -> str:
        return "event_pressure"

    @property
    def provider_mode(self) -> ProviderMode:
        return ProviderMode.MOCK

    def _fetch_real(self, destination_id: str, date: str) -> IngestedObservation:
        raise NotImplementedError(
            "No structured event calendar API exists for these Himalayan destinations. "
            "Implement when WBTDC or a regional event aggregator exposes a machine-readable API."
        )

    def _fetch_mock(self, destination_id: str, date: str) -> IngestedObservation:
        dest = destination_id.lower().strip()
        try:
            month = int(date.split("-")[1])
        except (IndexError, ValueError):
            month = datetime.now().month

        events = DESTINATION_ANNUAL_EVENTS.get(dest, [])
        active_events = [e for e in events if e["month"] == month]

        base_pressure = 10.0
        event_boost = sum(e["pressure_boost"] for e in active_events)
        event_pressure = min(100.0, base_pressure + event_boost)

        event_names = ", ".join(e["name"] for e in active_events) if active_events else "No major events"

        return IngestedObservation(
            destination_id=dest,
            date=date,
            signal_name=self.signal_name,
            signal_value=round(event_pressure, 1),
            raw_value=float(len(active_events)),
            raw_unit="concurrent_events",
            source="Mock Event Calendar (WBTDC Festival Schedule Analog)",
            provider_mode=ProviderMode.MOCK,
            timestamp=datetime.now(timezone.utc),
            confidence=0.80,
            data_quality="MEDIUM",
            notes=(
                f"Simulated event pressure (MOCK): {event_names}. "
                f"Based on annual Himalayan tourism festival calendar analog. "
                f"NOT a live event API. WBTDC/official event API not yet connected."
            ),
        )


event_ingestor = EventIngestor()
