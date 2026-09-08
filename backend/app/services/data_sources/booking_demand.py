"""
Booking Demand Provider for Yatri Setu.
Measures forward reservation velocity, advance room bookings,
and short-term inquiry conversion rates.
"""
from typing import Optional, Dict
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading


DESTINATION_BOOKING_VELOCITY: Dict[str, Dict] = {
    "darjeeling": {
        "score": 88.0,
        "daily_bookings": 320,
        "status": "Critical Demand / Rapid Sellout"
    },
    "kalimpong": {
        "score": 52.0,
        "daily_bookings": 85,
        "status": "Steady Demand / Moderate Pace"
    },
    "mirik": {
        "score": 42.0,
        "daily_bookings": 40,
        "status": "Balanced Demand / Weekend Spikes"
    },
    "lava": {
        "score": 28.0,
        "daily_bookings": 18,
        "status": "Available / Ample Inventory"
    },
    "lolegaon": {
        "score": 22.0,
        "daily_bookings": 12,
        "status": "Quiet / High Availability"
    },
    "rishop": {
        "score": 19.0,
        "daily_bookings": 9,
        "status": "Secluded / Ample Village Capacity"
    }
}


class MockBookingDemandProvider(BaseDataSourceProvider):
    """
    Simulates forward booking pace and reservation demand velocity.
    Can be replaced with CRS/Channel Manager (SiteMinder/RateGain) integration.
    """
    PROVIDER_TYPE = "MOCK"

    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        dest_clean = destination_id.lower().strip()
        info = DESTINATION_BOOKING_VELOCITY.get(
            dest_clean,
            {"score": 35.0, "daily_bookings": 25, "status": "Moderate Demand"}
        )

        return DataSourceReading(
            value=info["score"],
            available=True,
            source="MOCK_BOOKING_INTAKE_ENGINE",
            confidence=0.91,
            raw_value=float(info["daily_bookings"]),
            unit="confirmed_bookings_per_day",
            provider_mode="MOCK",
            data_quality="HIGH",
            signal_type="BOOKING_DEMAND",
            notes=f"Booking velocity: {info['status']} ({info['daily_bookings']} rooms/day)"
        )


booking_demand_provider = MockBookingDemandProvider()
