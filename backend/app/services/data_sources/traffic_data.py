"""
Traffic & Corridor Pressure Provider for Yatri Setu.
Measures arterial mountain road bottlenecks, checkpoint delays,
and transit route saturation in Himalayan hill circuits.
"""
from typing import Optional, Dict
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading


# Base bottleneck indices for access corridors to each destination (0-100)
DESTINATION_TRAFFIC_PROFILES: Dict[str, Dict] = {
    "darjeeling": {
        "pressure": 82.0,
        "corridor": "Hill Cart Road (NH 55) & Ghoom Railway Intersection",
        "delay_minutes": 45,
        "status": "Heavy Congestion / Ghoom Chokepoint"
    },
    "kalimpong": {
        "pressure": 54.0,
        "corridor": "NH 10 Teesta Bridge / 10th Mile",
        "delay_minutes": 20,
        "status": "Moderate Flow / Teesta Traffic Controls"
    },
    "mirik": {
        "pressure": 38.0,
        "corridor": "Mirik-Kurseong Ridge Road",
        "delay_minutes": 10,
        "status": "Smooth Transit / Occasional Viewpoint Stalls"
    },
    "lava": {
        "pressure": 24.0,
        "corridor": "Algarah-Lava Pine Forest Road",
        "delay_minutes": 5,
        "status": "Free Flowing Mountain Highway"
    },
    "lolegaon": {
        "pressure": 18.0,
        "corridor": "Lava-Lolegaon Heritage Forest Stretch",
        "delay_minutes": 0,
        "status": "Uncongested Forest Trail"
    },
    "rishop": {
        "pressure": 15.0,
        "corridor": "Upper Rishop Eco-Trail",
        "delay_minutes": 0,
        "status": "Pedestrian & 4x4 Only / Zero Jam"
    }
}


class MockTrafficDataProvider(BaseDataSourceProvider):
    """
    Simulates real-time corridor congestion and bottleneck delays.
    Can be swapped with Google Distance Matrix / TomTom Traffic API.
    """
    PROVIDER_TYPE = "MOCK"

    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        dest_clean = destination_id.lower().strip()
        profile = DESTINATION_TRAFFIC_PROFILES.get(
            dest_clean,
            {
                "pressure": 30.0,
                "corridor": "Regional Hill Arterial",
                "delay_minutes": 10,
                "status": "Normal Mountain Transit"
            }
        )

        return DataSourceReading(
            value=profile["pressure"],
            available=True,
            source="MOCK_REGIONAL_TRAFFIC_TELEMETRY",
            confidence=0.90,
            raw_value=float(profile["delay_minutes"]),
            unit="minutes_delay",
            provider_mode="MOCK",
            data_quality="HIGH",
            signal_type="TRAFFIC",
            notes=f"{profile['corridor']}: {profile['status']} (+{profile['delay_minutes']}m delay)"
        )


traffic_data_provider = MockTrafficDataProvider()
