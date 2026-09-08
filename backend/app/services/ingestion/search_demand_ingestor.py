"""
Search Demand Ingestor — Yatri Setu First-Party Signal (Milestone 6B).

SOURCE: "Yatri Setu Network"

Measures search query velocity and destination interest signals within the
Yatri Setu platform. This is a leading indicator: search demand typically
precedes booking demand by 3–10 days, making it a valuable predictive feature.

IMPORTANT DISCLAIMER:
  This reflects ONLY search activity within the Yatri Setu platform.
  It is NOT Google Trends data, state tourism portal traffic, or any nationwide measurement.
  Always labeled "Yatri Setu Network" — never misrepresented as third-party trend data.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.services.ingestion.base_ingestor import (
    BaseIngestor, IngestedObservation, ProviderMode
)

logger = logging.getLogger(__name__)

# Platform search demand profiles (normalized score + raw daily search count)
PLATFORM_SEARCH_PROFILES = {
    "darjeeling":  {"score": 92.0, "daily_searches": 4200, "trend": "Surging"},
    "kalimpong":   {"score": 58.0, "daily_searches": 980,  "trend": "Rising"},
    "mirik":       {"score": 46.0, "daily_searches": 620,  "trend": "Stable"},
    "lava":        {"score": 34.0, "daily_searches": 290,  "trend": "Moderate"},
    "lolegaon":    {"score": 28.0, "daily_searches": 210,  "trend": "Low"},
    "rishop":      {"score": 24.0, "daily_searches": 175,  "trend": "Niche / Discovery"},
}


class SearchDemandIngestor(BaseIngestor):
    """
    Ingests search demand (platform search velocity) as a leading crowd pressure indicator.

    Source: "Yatri Setu Network" — platform internal search index only.
    Real mode: Would connect to platform search analytics API.
    Mock mode: Deterministic simulation using configured search velocity profiles.
    """

    @property
    def source_label(self) -> str:
        return "Yatri Setu Network"

    @property
    def signal_name(self) -> str:
        return "search_demand"

    @property
    def provider_mode(self) -> ProviderMode:
        return ProviderMode.MOCK

    def _fetch_real(self, destination_id: str, date: str) -> IngestedObservation:
        raise NotImplementedError(
            "Real search demand ingestor requires connection to the Yatri Setu "
            "search analytics pipeline. Not yet implemented."
        )

    def _fetch_mock(self, destination_id: str, date: str) -> IngestedObservation:
        dest = destination_id.lower().strip()
        profile = PLATFORM_SEARCH_PROFILES.get(
            dest,
            {"score": 35.0, "daily_searches": 300, "trend": "Moderate"}
        )
        score = float(profile["score"])
        searches = profile["daily_searches"]
        trend = profile["trend"]

        return IngestedObservation(
            destination_id=dest,
            date=date,
            signal_name=self.signal_name,
            signal_value=score,
            raw_value=float(searches),
            raw_unit="platform_search_queries_per_day",
            source="Yatri Setu Network",
            provider_mode=ProviderMode.MOCK,
            timestamp=datetime.now(timezone.utc),
            confidence=0.88,
            data_quality="HIGH",
            notes=(
                f"Platform search velocity (MOCK): {trend} — "
                f"{searches:,} queries/day. "
                f"Leading indicator: 3–10 day booking precursor. "
                f"Yatri Setu Network signal only; not Google Trends or national data."
            ),
        )


search_demand_ingestor = SearchDemandIngestor()
