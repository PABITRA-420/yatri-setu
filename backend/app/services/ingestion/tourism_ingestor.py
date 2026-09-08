"""
Tourism Footfall Ingestor (Milestone 6B).

Attempts to ingest historical tourism footfall data from legitimate public sources.

Real Data Assessment:
  - Ministry of Tourism (India) provides annual state-level tourism statistics via
    their Tourism Statistics publications, but these are annual aggregates — NOT
    real-time or destination-level data suitable for ML training.
  - West Bengal Tourism Development Corporation (WBTDC) does not expose a public API.
  - No legitimate, programmatically accessible real-time tourism footfall API exists
    for these specific Himalayan micro-destinations as of 2026.

CONCLUSION:
  Provider mode is MOCK. No government endpoint is fabricated.
  If/when a real API becomes available, implement _fetch_real() accordingly.

Source clearly labeled: "Mock Tourism Simulator (WBTDC Analog)"
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.services.ingestion.base_ingestor import (
    BaseIngestor, IngestedObservation, ProviderMode
)

logger = logging.getLogger(__name__)

# Tourism footfall profiles modeled after WBTDC annual reports and regional estimates
# These are SIMULATED profiles, not live government data
TOURISM_FOOTFALL_PROFILES = {
    "darjeeling":  {"annual_visitors": 850_000, "peak_score": 95.0, "baseline_score": 70.0},
    "kalimpong":   {"annual_visitors": 180_000, "peak_score": 68.0, "baseline_score": 45.0},
    "mirik":       {"annual_visitors": 140_000, "peak_score": 58.0, "baseline_score": 38.0},
    "lava":        {"annual_visitors": 45_000,  "peak_score": 38.0, "baseline_score": 25.0},
    "lolegaon":    {"annual_visitors": 38_000,  "peak_score": 32.0, "baseline_score": 20.0},
    "rishop":      {"annual_visitors": 28_000,  "peak_score": 28.0, "baseline_score": 18.0},
}


class TourismIngestor(BaseIngestor):
    """
    Simulates historical tourism footfall for Himalayan destinations.

    MOCK-only provider: No legitimate real-time government API exists for these
    micro-destinations. The provider is explicitly labeled as a simulation.
    """

    @property
    def source_label(self) -> str:
        return "Mock Tourism Simulator (WBTDC Analog)"

    @property
    def signal_name(self) -> str:
        return "historical_footfall"

    @property
    def provider_mode(self) -> ProviderMode:
        return ProviderMode.MOCK

    def _fetch_real(self, destination_id: str, date: str) -> IngestedObservation:
        raise NotImplementedError(
            "No legitimate real-time tourism footfall API exists for these Himalayan "
            "micro-destinations. Implement when WBTDC or Ministry of Tourism provides "
            "a programmatically accessible endpoint. DO NOT fabricate a government URL."
        )

    def _fetch_mock(self, destination_id: str, date: str) -> IngestedObservation:
        dest = destination_id.lower().strip()
        profile = TOURISM_FOOTFALL_PROFILES.get(
            dest,
            {"annual_visitors": 50_000, "peak_score": 40.0, "baseline_score": 25.0}
        )

        score = profile["baseline_score"]
        annual = profile["annual_visitors"]

        return IngestedObservation(
            destination_id=dest,
            date=date,
            signal_name=self.signal_name,
            signal_value=score,
            raw_value=float(annual),
            raw_unit="estimated_annual_visitors",
            source="Mock Tourism Simulator (WBTDC Analog)",
            provider_mode=ProviderMode.MOCK,
            timestamp=datetime.now(timezone.utc),
            confidence=0.75,
            data_quality="MEDIUM",
            notes=(
                f"Simulated footfall (MOCK): ~{annual:,} estimated annual visitors. "
                f"No live government API connected. "
                f"Based on analog of WBTDC regional tourism statistics (annual aggregates). "
                f"NOT real-time or officially endorsed data."
            ),
        )


tourism_ingestor = TourismIngestor()
