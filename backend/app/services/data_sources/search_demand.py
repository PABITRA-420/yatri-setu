"""
Search Demand Provider for Yatri Setu.
Simulates forward-looking tourist intent via search volume, OTA inquiries,
and travel query velocity for Himalayan destinations.
"""
from datetime import datetime, date
from typing import Optional, Dict
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading


# Baseline monthly search interest multiplier (indexed around 1.0)
MONTHLY_SEARCH_MULTIPLIER: Dict[int, float] = {
    1: 0.85,   # Jan (post-new-year cooling)
    2: 0.90,   # Feb
    3: 1.15,   # Mar (spring surge)
    4: 1.35,   # Apr (peak summer escape search)
    5: 1.45,   # May (peak summer query volume)
    6: 1.10,   # Jun (early monsoon dip)
    7: 0.65,   # Jul (monsoon bottom)
    8: 0.60,   # Aug (landslide concerns)
    9: 1.05,   # Sep (autumn puja prep queries)
    10: 1.40,  # Oct (Durga puja peak searches)
    11: 1.25,  # Nov (clear mountain view queries)
    12: 1.35   # Dec (winter holiday / snow search)
}

# Base search score per destination (0-100 scale)
DESTINATION_BASE_SEARCH: Dict[str, float] = {
    "darjeeling": 82.0,  # Highest organic search volume
    "kalimpong": 52.0,
    "mirik": 42.0,
    "lava": 28.0,
    "lolegaon": 22.0,
    "rishop": 18.0
}


class MockSearchDemandProvider(BaseDataSourceProvider):
    """
    Provides normalized search interest index (0-100) reflecting
    pre-booking interest on search engines and OTA aggregators.
    """
    PROVIDER_TYPE = "MOCK"

    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        dest_clean = destination_id.lower().strip()
        base_search = DESTINATION_BASE_SEARCH.get(dest_clean, 35.0)

        target_month = date.today().month
        if date_str:
            try:
                target_month = datetime.strptime(date_str, "%Y-%m-%d").month
            except ValueError:
                pass

        multiplier = MONTHLY_SEARCH_MULTIPLIER.get(target_month, 1.0)
        calculated_score = min(100.0, max(5.0, base_search * multiplier))

        trend_label = "Surging" if calculated_score > 75 else ("Moderate" if calculated_score > 40 else "Low")

        # Track leading indicator metrics
        query_index = round(calculated_score * 12.5, 0)
        unique_searchers = int(query_index * 0.78)
        booking_conversion = 0.08 if calculated_score > 60 else 0.14
        period_change = round((multiplier - 1.0) * 100.0, 1)

        return DataSourceReading(
            value=round(calculated_score, 1),
            available=True,
            source="MOCK_SEARCH_DEMAND_LEADING_INDEX",
            confidence=0.88,
            raw_value=query_index,
            unit="query_velocity_index",
            provider_mode="MOCK",
            data_quality="HIGH",
            signal_type="SEARCH_DEMAND",
            notes=f"Leading indicator: {trend_label} intent ({unique_searchers} unique queries, {period_change:+.1f}% period change, {booking_conversion*100:.1f}% conversion)"
        )

    def get_demand_metrics(self, destination_id: str) -> dict:
        """Detailed demand observation tracking search leading indicators."""
        dest_clean = destination_id.lower().strip()
        base_search = DESTINATION_BASE_SEARCH.get(dest_clean, 35.0)
        target_month = date.today().month
        multiplier = MONTHLY_SEARCH_MULTIPLIER.get(target_month, 1.0)
        calculated_score = min(100.0, max(5.0, base_search * multiplier))
        query_index = int(calculated_score * 12.5)

        trend = "RISING" if multiplier > 1.1 else ("DECLINING" if multiplier < 0.9 else "STABLE")

        return {
            "destination_id": dest_clean,
            "search_count": query_index,
            "unique_searchers": int(query_index * 0.78),
            "booking_conversion": 0.08 if calculated_score > 60 else 0.14,
            "period_change_percent": round((multiplier - 1.0) * 100.0, 1),
            "trend": trend,
            "is_leading_indicator": True,
            "notes": "Leading demand indicator reflects forward booking intent, not instantaneous physical presence."
        }


search_demand_provider = MockSearchDemandProvider()

