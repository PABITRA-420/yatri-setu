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

    def build_feature_row(
        self,
        obs: Any,
        target_pressure: Optional[float] = None,
        feature_timestamp: Optional[str] = None,
        target_timestamp: Optional[str] = None,
        target_horizon_days: int = 0
    ) -> Dict[str, Any]:
        """Extracts a structured feature dictionary from a single observation with explicit temporal provenance."""
        date_str = getattr(obs, "date", None) or getattr(obs, "date_bucket", None)
        dest_id = getattr(obs, "destination_id", "")
        dest_clean = dest_id.lower().strip()

        dt = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()
        weekday = dt.weekday()
        is_weekend = 1 if weekday in (4, 5, 6) else 0
        month = dt.month
        day_of_year = dt.timetuple().tm_yday

        is_summer = 1 if month in (4, 5, 6) else 0
        is_autumn = 1 if month in (9, 10, 11) else 0

        # Safe extraction of signals (handles both attribute names and None values)
        footfall = getattr(obs, "historical_footfall", None)
        if footfall is None:
            footfall = getattr(obs, "footfall", None)

        accom = getattr(obs, "accommodation_occupancy", None)
        booking = getattr(obs, "booking_demand", None)
        search = getattr(obs, "search_demand", None)
        event = getattr(obs, "event_pressure", None)
        holiday = getattr(obs, "holiday_pressure", None)
        weather = getattr(obs, "weather_pressure", None)
        traffic = getattr(obs, "traffic_pressure", None)

        # Leading indicator ratio (safe against None and division by zero)
        if search is not None and booking is not None:
            ratio = round(search / (booking + 1e-3), 2)
        else:
            ratio = None

        # Resolve target pressure
        if target_pressure is None:
            target_pressure = getattr(obs, "observed_pressure", None)
            if target_pressure is None:
                target_pressure = getattr(obs, "current_crowd_pressure", None)

        feat_time = feature_timestamp or date_str
        targ_time = target_timestamp or date_str

        row: Dict[str, Any] = {
            "date": date_str,
            "feature_timestamp": feat_time,
            "target_timestamp": targ_time,
            "target_horizon_days": target_horizon_days,
            "destination_id": dest_clean,
            "historical_footfall": footfall,
            "accommodation_occupancy": accom,
            "booking_demand": booking,
            "search_demand": search,
            "event_pressure": event,
            "holiday_pressure": holiday,
            "weather_pressure": weather,
            "traffic_pressure": traffic,
            "day_of_week": weekday,
            "is_weekend": is_weekend,
            "month": month,
            "day_of_year": day_of_year,
            "search_to_booking_ratio": ratio,
            "is_peak_summer": is_summer,
            "is_peak_autumn": is_autumn,
            "target_pressure": target_pressure,
        }

        # Destination one-hot encoding
        for dest_name in self.DESTINATION_INDEX:
            row[f"dest_{dest_name}"] = 1 if dest_clean == dest_name else 0

        return row

    def build_features(self, observations: List[Any]) -> List[Dict[str, Any]]:
        """Transform a sequence of observations into feature dictionaries."""
        return [self.build_feature_row(obs) for obs in observations]

