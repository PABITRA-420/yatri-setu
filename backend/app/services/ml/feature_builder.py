"""
Feature Builder Interface and Standard Transformer (Milestone 6A).
Transforms raw historical observations into structured feature vectors for ML models.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.dataset_evaluation import HistoricalObservation


class BaseFeatureBuilder(ABC):
    """Abstract interface for extracting tabular feature matrices from crowd observations."""

    @abstractmethod
    def build_features(self, observations: List[HistoricalObservation]) -> List[Dict[str, Any]]:
        """Transform a sequence of observations into feature dictionaries."""
        pass

    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """Returns the ordered list of feature column names."""
        pass


class StandardFeatureBuilder(BaseFeatureBuilder):
    """
    Standard temporal and multi-signal feature extractor.
    Extracts calendar cycles, weekend indicators, leading signal ratios, and destination archetypes.
    """

    FEATURE_NAMES = [
        "historical_footfall",
        "accommodation_occupancy",
        "booking_demand",
        "search_demand",
        "event_pressure",
        "holiday_pressure",
        "weather_pressure",
        "traffic_pressure",
        "day_of_week",
        "is_weekend",
        "month",
        "day_of_year",
        "search_to_booking_ratio",
        "is_peak_summer",
        "is_peak_autumn",
    ]

    DESTINATION_INDEX = {
        "darjeeling": 0,
        "kalimpong": 1,
        "mirik": 2,
        "lava": 3,
        "lolegaon": 4,
        "rishop": 5,
    }

    def get_feature_names(self) -> List[str]:
        return list(self.FEATURE_NAMES) + [f"dest_{d}" for d in self.DESTINATION_INDEX]

    def build_features(self, observations: List[HistoricalObservation]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []

        for obs in observations:
            dt = datetime.strptime(obs.date, "%Y-%m-%d").date()
            weekday = dt.weekday()
            is_weekend = 1 if weekday in (4, 5, 6) else 0
            month = dt.month
            day_of_year = dt.timetuple().tm_yday

            # Leading indicator ratio
            ratio = round(obs.search_demand / (obs.booking_demand + 1e-3), 2)

            is_summer = 1 if month in (4, 5, 6) else 0
            is_autumn = 1 if month in (9, 10, 11) else 0

            row: Dict[str, Any] = {
                "date": obs.date,
                "destination_id": obs.destination_id,
                "historical_footfall": obs.historical_footfall,
                "accommodation_occupancy": obs.accommodation_occupancy,
                "booking_demand": obs.booking_demand,
                "search_demand": obs.search_demand,
                "event_pressure": obs.event_pressure,
                "holiday_pressure": obs.holiday_pressure,
                "weather_pressure": obs.weather_pressure,
                "traffic_pressure": obs.traffic_pressure,
                "day_of_week": weekday,
                "is_weekend": is_weekend,
                "month": month,
                "day_of_year": day_of_year,
                "search_to_booking_ratio": ratio,
                "is_peak_summer": is_summer,
                "is_peak_autumn": is_autumn,
                "target_pressure": obs.observed_pressure,
            }

            # Destination one-hot encoding
            for dest_name in self.DESTINATION_INDEX:
                row[f"dest_{dest_name}"] = 1 if obs.destination_id.lower().strip() == dest_name else 0

            rows.append(row)

        return rows
