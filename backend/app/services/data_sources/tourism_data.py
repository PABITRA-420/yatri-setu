"""
Tourism Data Provider — Historical Footfall Signal.

MOCK provider uses curated seasonal footfall profiles.
Future REAL provider would connect to state tourism board APIs.
"""
from typing import Optional
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading

# Seeded annual average footfall pressure (0-100) per destination
_FOOTFALL_PROFILES = {
    "darjeeling":  92.0,
    "kalimpong":   45.0,
    "lava":        25.0,
    "lolegaon":    18.0,
    "rishop":      15.0,
    "mirik":       40.0,
}


class MockTourismDataProvider(BaseDataSourceProvider):
    """
    Deterministic historical footfall provider.
    Source: Curated seasonal averages (NOT live government data).
    """
    PROVIDER_TYPE = "MOCK"

    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        dest = destination_id.lower().strip()
        value = _FOOTFALL_PROFILES.get(dest, 50.0)
        return DataSourceReading(
            value=value,
            available=True,
            source="MOCK:tourism_historical",
            confidence=0.90,
            raw_value=value,
            unit="index_0_100",
            provider_mode="MOCK",
            data_quality="HIGH",
            signal_type="HISTORICAL_FOOTFALL",
            notes="Historical seasonal footfall profile (mock — not live state tourism data)"
        )


# Default provider (swap to RealTourismDataProvider when API is available)
tourism_data_provider = MockTourismDataProvider()
