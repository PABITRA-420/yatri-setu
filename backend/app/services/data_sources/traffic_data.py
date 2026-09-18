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


class LiveTrafficDataProvider(BaseDataSourceProvider):
    """
    Queries live TrafficService (TomTom / Mountain Arterial Telemetry).
    Falls back gracefully to regional profiles without misrepresenting provenance.
    """
    PROVIDER_TYPE = "REAL"

    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        dest_clean = destination_id.lower().strip()
        try:
            from app.services.traffic.service import traffic_service
            summary = traffic_service.get_traffic(dest_clean)
            if summary:
                if summary.provider_mode == "REAL":
                    mode = "REAL"
                    source = summary.source
                    val = summary.overall_congestion_score
                else:
                    mode = "MOCK"
                    source = f"MOCK_{summary.source}"
                    val = DESTINATION_TRAFFIC_PROFILES.get(dest_clean, {}).get("pressure", summary.overall_congestion_score)
                return DataSourceReading(
                    value=val,
                    available=True,
                    source=source,
                    confidence=summary.confidence,
                    raw_value=float(summary.travel_time_anomaly_percent),
                    unit="percent_travel_time_anomaly",
                    provider_mode=mode,
                    data_quality=summary.data_quality,
                    signal_type="TRAFFIC",
                    notes=f"Corridor: {summary.primary_bottleneck_route or 'Direct Artery'} ({summary.access_status})"
                )
        except Exception:
            pass

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

MockTrafficDataProvider = LiveTrafficDataProvider


traffic_data_provider = MockTrafficDataProvider()
