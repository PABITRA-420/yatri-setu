"""
Booking Demand Ingestor — Yatri Setu First-Party Signal (Milestone 6B).

SOURCE: "Yatri Setu Network"

This signal is derived from booking transactions flowing through the
Yatri Setu platform itself. It reflects platform-level booking velocity
and reservation intake for the six monitored Himalayan destinations.

IMPORTANT DISCLAIMER:
  This is NOT a nationwide booking measurement.
  This reflects ONLY bookings transacted via the Yatri Setu platform.
  Source is always labeled "Yatri Setu Network" — never as "India Tourism" or equivalent.

Real mode: Reads aggregated booking counts from the platform's internal DB/cache.
Mock mode: Deterministic simulation using configured booking velocity profiles.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
import random

from app.services.ingestion.base_ingestor import (
    BaseIngestor, IngestedObservation, ProviderMode
)
from app.core.config import settings

logger = logging.getLogger(__name__)

# First-party booking velocity profiles (per destination)
# These represent typical daily confirmed bookings on the Yatri Setu platform.
PLATFORM_BOOKING_PROFILES = {
    "darjeeling":  {"score": 88.0, "daily_bookings": 320, "status": "Critical Demand / Rapid Sellout"},
    "kalimpong":   {"score": 52.0, "daily_bookings": 85,  "status": "Steady Demand / Moderate Pace"},
    "mirik":       {"score": 42.0, "daily_bookings": 40,  "status": "Balanced Demand / Weekend Spikes"},
    "lava":        {"score": 28.0, "daily_bookings": 18,  "status": "Available / Ample Inventory"},
    "lolegaon":    {"score": 22.0, "daily_bookings": 12,  "status": "Quiet / High Availability"},
    "rishop":      {"score": 19.0, "daily_bookings": 9,   "status": "Secluded / Ample Village Capacity"},
}


class BookingIngestor(BaseIngestor):
    """
    Ingests booking demand from the Yatri Setu platform (first-party signal).

    Provider mode: MOCK (default) or REAL (when platform DB is connected).
    Source label: "Yatri Setu Network" — always. Never misrepresent this as external data.
    """

    @property
    def source_label(self) -> str:
        return "Yatri Setu Network"

    @property
    def signal_name(self) -> str:
        return "booking_demand"

    @property
    def provider_mode(self) -> ProviderMode:
        # Real mode would require a live platform DB connection
        # Currently always MOCK until a production API is wired in
        return ProviderMode.MOCK

    def _fetch_real(self, destination_id: str, date: str) -> IngestedObservation:
        """
        In production, this would query the Yatri Setu platform's booking aggregation API.
        Currently raises NotImplementedError to prevent silent fake "REAL" labeling.
        """
        raise NotImplementedError(
            "Real booking ingestor is not yet connected to a live platform API. "
            "Set provider_mode to MOCK or wire a production booking DB connection."
        )

    def _fetch_mock(self, destination_id: str, date: str) -> IngestedObservation:
        dest = destination_id.lower().strip()
        profile = PLATFORM_BOOKING_PROFILES.get(
            dest, {"score": 35.0, "daily_bookings": 25, "status": "Moderate Demand"}
        )
        score = float(profile["score"])
        daily = profile["daily_bookings"]

        return IngestedObservation(
            destination_id=dest,
            date=date,
            signal_name=self.signal_name,
            signal_value=score,
            raw_value=float(daily),
            raw_unit="confirmed_bookings_per_day",
            source="Yatri Setu Network",
            provider_mode=ProviderMode.MOCK,
            timestamp=datetime.now(timezone.utc),
            confidence=0.91,
            data_quality="HIGH",
            notes=(
                f"Platform booking velocity (MOCK): {profile['status']} — "
                f"{daily} rooms/day. "
                f"Yatri Setu Network signal only; not a nationwide measurement."
            ),
        )


booking_ingestor = BookingIngestor()
