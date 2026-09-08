"""
Accommodation Occupancy Data Provider.

Tracks total capacity vs occupied rooms to derive
an accommodation pressure index (0-100).

MOCK provider uses seeded prototype occupancy data.
Future REAL provider would integrate with OTA APIs / PMS systems.
"""
from typing import Optional
from dataclasses import dataclass
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading

@dataclass
class AccommodationProfile:
    total_capacity: int
    occupied: int
    pressure_classification: str

    @property
    def occupancy_percent(self) -> float:
        if self.total_capacity == 0:
            return 0.0
        return round((self.occupied / self.total_capacity) * 100, 1)

    @property
    def pressure_index(self) -> float:
        """Map occupancy% → pressure index 0-100"""
        pct = self.occupancy_percent
        if pct >= 95:
            return 98.0
        elif pct >= 85:
            return 88.0
        elif pct >= 70:
            return 72.0
        elif pct >= 50:
            return 52.0
        elif pct >= 30:
            return 32.0
        else:
            return 18.0


_ACCOMMODATION_PROFILES = {
    "darjeeling": AccommodationProfile(
        total_capacity=3200, occupied=2912,
        pressure_classification="CRITICAL"
    ),
    "kalimpong": AccommodationProfile(
        total_capacity=820, occupied=369,
        pressure_classification="MODERATE"
    ),
    "lava": AccommodationProfile(
        total_capacity=280, occupied=62,
        pressure_classification="LOW"
    ),
    "lolegaon": AccommodationProfile(
        total_capacity=190, occupied=38,
        pressure_classification="LOW"
    ),
    "rishop": AccommodationProfile(
        total_capacity=160, occupied=32,
        pressure_classification="LOW"
    ),
    "mirik": AccommodationProfile(
        total_capacity=540, occupied=216,
        pressure_classification="MODERATE"
    ),
}


class MockAccommodationDataProvider(BaseDataSourceProvider):
    """
    Deterministic accommodation occupancy provider.
    Source: Seeded prototype data (NOT live OTA/PMS data).
    """
    PROVIDER_TYPE = "MOCK"

    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        dest = destination_id.lower().strip()
        profile = _ACCOMMODATION_PROFILES.get(dest)
        if not profile:
            return DataSourceReading(
                value=50.0,
                available=True,
                source="MOCK: Yatri Setu network occupancy",
                confidence=0.50,
                raw_value=50.0,
                unit="occupancy_percent",
                provider_mode="MOCK",
                data_quality="MEDIUM",
                signal_type="ACCOMMODATION",
                notes="No platform listing baseline — using neutral network occupancy"
            )
        return DataSourceReading(
            value=profile.pressure_index,
            available=True,
            source="MOCK: Yatri Setu network occupancy",
            confidence=0.88,
            raw_value=profile.occupancy_percent,
            unit="occupancy_percent",
            provider_mode="MOCK",
            data_quality="HIGH",
            signal_type="ACCOMMODATION",
            notes=f"Yatri Setu network occupancy: {profile.occupied}/{profile.total_capacity} platform rooms booked ({profile.occupancy_percent}% | {profile.pressure_classification})"
        )


    def get_platform_occupancy(self, destination_id: str) -> dict:
        """
        Calculate platform-specific accommodation occupancy for Yatri Setu network.
        Explicitly clarifies this is internal network inventory, not nationwide hotel data.
        """
        dest = destination_id.lower().strip()
        profile = _ACCOMMODATION_PROFILES.get(dest)
        if not profile:
            return {
                "destination_id": dest,
                "total_capacity": 100,
                "occupied_capacity": 50,
                "occupancy_percent": 50.0,
                "pressure": 50.0,
                "source_label": "Yatri Setu network occupancy",
                "is_nationwide": False
            }
        return {
            "destination_id": dest,
            "total_capacity": profile.total_capacity,
            "occupied_capacity": profile.occupied,
            "occupancy_percent": profile.occupancy_percent,
            "pressure": profile.pressure_index,
            "source_label": "Yatri Setu network occupancy",
            "is_nationwide": False
        }

    def get_profile(self, destination_id: str) -> Optional[AccommodationProfile]:
        return _ACCOMMODATION_PROFILES.get(destination_id.lower().strip())


accommodation_data_provider = MockAccommodationDataProvider()

