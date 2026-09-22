"""
Feature Builder Interface and Standard Transformer (Milestone 6A).
Transforms raw historical observations into structured feature vectors for ML models.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date, timezone
from typing import List, Dict, Any, Optional, Tuple
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


SCHEMA_VERSION = "2.0.0"


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
        "target_horizon_days",
    ]

    DESTINATION_INDEX = {
        "darjeeling": 0,
        "kalimpong": 1,
        "mirik": 2,
        "lava": 3,
        "lolegaon": 4,
        "rishop": 5,
    }

    SCHEMA_VERSION = "2.0.0"

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

    def build_inference_features(
        self,
        destination_id: str,
        target_date: date,
        feature_date: Optional[date] = None,
        target_horizon_days: int = 1,
        horizon_days: Optional[int] = None,
        current_telemetry: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Unified inference feature builder.
        Extracts genuine telemetry available at feature_date (T)
        and deterministic calendar/event context for target_date (T + H).
        Missing telemetry remains None (never filled with invented numbers).
        """
        effective_horizon = horizon_days if horizon_days is not None else target_horizon_days
        dest_clean = destination_id.lower().strip()

        feat_dt = feature_date or datetime.now(timezone.utc).date()
        feat_date_str = feat_dt.strftime("%Y-%m-%d")
        targ_date_str = target_date.strftime("%Y-%m-%d")

        # Calendar features evaluated for target_date (T + H)
        weekday = target_date.weekday()
        is_weekend = 1 if weekday in (4, 5, 6) else 0
        month = target_date.month
        day_of_year = target_date.timetuple().tm_yday
        is_summer = 1 if month in (4, 5, 6) else 0
        is_autumn = 1 if month in (9, 10, 11) else 0

        from app.services.holiday_engine import holiday_engine
        from app.services.events_engine import events_engine

        hol_res = holiday_engine.calculate_holiday_pressure(target_date)
        holiday_val = float(hol_res.get("score", 0.0))

        ev_res = events_engine.calculate_event_pressure(dest_clean, target_date)
        event_val = float(ev_res.get("score", 0.0))

        # Telemetry observed at prediction time T
        telemetry = dict(current_telemetry) if current_telemetry else {}
        if not telemetry:
            try:
                from app.services.crowd_engine_v2 import crowd_engine_v2
                pres = crowd_engine_v2.calculate_pressure(dest_clean, feat_date_str)
                # Extract genuine readings
                for s in pres.signals:
                    if s.available and s.source != "OFFLINE":
                        telemetry[s.signal_key] = s.value
            except Exception:
                pass

        footfall = telemetry.get("historical_footfall")
        accom = telemetry.get("accommodation_occupancy")
        booking = telemetry.get("booking_demand")
        search = telemetry.get("search_demand")
        weather = telemetry.get("weather_pressure")
        traffic = telemetry.get("traffic_pressure")

        ratio = round(search / (booking + 1e-3), 2) if search is not None and booking is not None else None

        row: Dict[str, Any] = {
            "date": feat_date_str,
            "feature_timestamp": feat_date_str,
            "target_timestamp": targ_date_str,
            "target_horizon_days": effective_horizon,
            "destination_id": dest_clean,
            "historical_footfall": footfall,
            "accommodation_occupancy": accom,
            "booking_demand": booking,
            "search_demand": search,
            "event_pressure": event_val,
            "holiday_pressure": holiday_val,
            "weather_pressure": weather,
            "traffic_pressure": traffic,
            "day_of_week": weekday,
            "is_weekend": is_weekend,
            "month": month,
            "day_of_year": day_of_year,
            "search_to_booking_ratio": ratio,
            "is_peak_summer": is_summer,
            "is_peak_autumn": is_autumn,
            "target_pressure": None,  # At inference time, target is unknown
        }

        # Destination one-hot encoding
        for dest_name in self.DESTINATION_INDEX:
            row[f"dest_{dest_name}"] = 1 if dest_clean == dest_name else 0

        return row

    def validate_feature_schema(self, features: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validates that a feature dictionary contains all required feature names."""
        missing = [f for f in self.get_feature_names() if f not in features]
        return len(missing) == 0, missing


