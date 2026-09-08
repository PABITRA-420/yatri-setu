"""
Accommodation Occupancy Ingestor — Yatri Setu First-Party Signal (Milestone 6B).

SOURCE: "Yatri Setu Network"

Reflects real-time accommodation occupancy rates across properties registered
on the Yatri Setu platform. This is a first-party signal drawn from the platform's
homestay/hotel inventory and check-in/check-out tracking.

IMPORTANT DISCLAIMER:
  This is NOT a district-wide or state-wide occupancy survey.
  This reflects ONLY properties registered on the Yatri Setu platform.
  Always labeled as "Yatri Setu Network" — never misrepresented as official tourism data.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.services.ingestion.base_ingestor import (
    BaseIngestor, IngestedObservation, ProviderMode
)

logger = logging.getLogger(__name__)

# Platform accommodation occupancy profiles (% of registered capacity filled)
PLATFORM_OCCUPANCY_PROFILES = {
    "darjeeling":  {"occupancy_pct": 94.0, "status": "Nearly Full / Limited Rooms", "registered_properties": 180},
    "kalimpong":   {"occupancy_pct": 61.0, "status": "Comfortable Occupancy",        "registered_properties": 72},
    "mirik":       {"occupancy_pct": 48.0, "status": "Moderate Occupancy",            "registered_properties": 45},
    "lava":        {"occupancy_pct": 31.0, "status": "Ample Availability",            "registered_properties": 28},
    "lolegaon":    {"occupancy_pct": 25.0, "status": "Low Occupancy / High Vacancy",  "registered_properties": 22},
    "rishop":      {"occupancy_pct": 22.0, "status": "Very Low Occupancy",            "registered_properties": 18},
}


class AccommodationIngestor(BaseIngestor):
    """
    Ingests accommodation occupancy from the Yatri Setu platform (first-party signal).

    Source: "Yatri Setu Network" (platform-registered properties only).
    Provider mode: MOCK until live property management system integration is wired in.
    """

    @property
    def source_label(self) -> str:
        return "Yatri Setu Network"

    @property
    def signal_name(self) -> str:
        return "accommodation_occupancy"

    @property
    def provider_mode(self) -> ProviderMode:
        return ProviderMode.MOCK

    def _fetch_real(self, destination_id: str, date: str) -> IngestedObservation:
        raise NotImplementedError(
            "Real accommodation ingestor is not yet connected to a property management API. "
            "Requires live PMS/channel manager integration."
        )

    def _fetch_mock(self, destination_id: str, date: str) -> IngestedObservation:
        dest = destination_id.lower().strip()
        profile = PLATFORM_OCCUPANCY_PROFILES.get(
            dest,
            {"occupancy_pct": 40.0, "status": "Moderate", "registered_properties": 30}
        )
        occupancy = float(profile["occupancy_pct"])
        props = profile["registered_properties"]

        return IngestedObservation(
            destination_id=dest,
            date=date,
            signal_name=self.signal_name,
            signal_value=occupancy,
            raw_value=occupancy,
            raw_unit="percent_occupied",
            source="Yatri Setu Network",
            provider_mode=ProviderMode.MOCK,
            timestamp=datetime.now(timezone.utc),
            confidence=0.90,
            data_quality="HIGH",
            notes=(
                f"Platform accommodation occupancy (MOCK): {profile['status']} — "
                f"{occupancy:.0f}% across {props} registered properties. "
                f"Yatri Setu Network signal only; not a district-wide survey."
            ),
        )


accommodation_ingestor = AccommodationIngestor()
