"""
Pressure Refresh Service for Yatri Setu (Milestone 7C).
Orchestrates live signals (Weather, Traffic, Demand, Events, Holidays, Occupancy),
calculates deterministic pressure with explainable top drivers,
tracks "Why pressure changed" deltas across refresh cycles,
and strictly separates route access status (OPEN, CAUTION, DISRUPTED) from crowd pressure.
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.weather.service import weather_service
from app.services.weather.schemas import WeatherObservation, WeatherImpactSignal
from app.services.traffic.service import traffic_service
from app.services.traffic.schemas import DestinationTrafficSummary, TrafficImpactSignal
from app.services.events_engine import events_engine
from app.services.holiday_engine import holiday_engine
from app.services.demand_aggregation_service import demand_aggregation_service

logger = logging.getLogger(__name__)

ALL_DESTINATIONS = ["darjeeling", "kalimpong", "lava", "lolegaon", "rishop", "mirik"]

# Baseline historical footfall weights and capacities
DESTINATION_CONFIG: Dict[str, Dict[str, Any]] = {
    "darjeeling": {"name": "Darjeeling", "baseline_footfall": 85.0, "occupancy_base": 88.0, "is_hub": True},
    "kalimpong": {"name": "Kalimpong", "baseline_footfall": 52.0, "occupancy_base": 55.0, "is_hub": False},
    "lava": {"name": "Lava", "baseline_footfall": 28.0, "occupancy_base": 32.0, "is_hub": False},
    "lolegaon": {"name": "Lolegaon", "baseline_footfall": 22.0, "occupancy_base": 25.0, "is_hub": False},
    "rishop": {"name": "Rishop", "baseline_footfall": 18.0, "occupancy_base": 20.0, "is_hub": False},
    "mirik": {"name": "Mirik", "baseline_footfall": 38.0, "occupancy_base": 42.0, "is_hub": False},
}


class PressureDriver(BaseModel):
    signal: str
    impact: float  # points contributed
    description: str


class PressureExplanation(BaseModel):
    destination_id: str
    pressure_level: str
    pressure_score: float
    top_drivers: List[PressureDriver]
    access_status: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class PressureChangeDriver(BaseModel):
    signal: str
    delta: float
    description: str


class PressureChangeSummary(BaseModel):
    destination_id: str
    pressure_delta: float
    previous_score: float
    current_score: float
    drivers: List[PressureChangeDriver]
    previous_refresh_at: Optional[datetime] = None
    current_refresh_at: datetime = Field(default_factory=datetime.utcnow)


class DestinationLiveConditions(BaseModel):
    destination_id: str
    destination_name: str
    condition_type: str = "CURRENT CONDITIONS"  # CURRENT CONDITIONS, FORECAST CONDITIONS, HISTORICAL BASELINE
    pressure_score: float
    pressure_level: str  # LOW, MODERATE, HIGH, CRITICAL
    access_status: str  # OPEN, CAUTION, DISRUPTED, UNKNOWN
    weather: WeatherObservation
    traffic: DestinationTrafficSummary
    weather_impact: WeatherImpactSignal
    traffic_impact: TrafficImpactSignal
    event_pressure: float
    holiday_pressure: float
    first_party_demand: float
    top_drivers: List[PressureDriver]
    pressure_change: Optional[PressureChangeSummary] = None
    provenance: str
    data_quality: str
    refreshed_at: datetime = Field(default_factory=datetime.utcnow)


def classify_pressure_level(score: float) -> str:
    if score >= 80.0:
        return "CRITICAL"
    elif score >= 60.0:
        return "HIGH"
    elif score >= 40.0:
        return "MODERATE"
    return "LOW"


class PressureRefreshService:
    """
    Coordinates multi-signal live telemetry, recalculates dynamic destination pressure,
    maintains historical snapshots for delta explanation, and supports date-specific queries.
    """

    def __init__(self):
        # Snapshots: destination_id -> dict of signal readings and computed score
        self._previous_snapshots: Dict[str, Dict[str, Any]] = {}
        self._current_snapshots: Dict[str, Dict[str, Any]] = {}
        self._last_refresh_time: Optional[datetime] = None
        self._rate_limit_cooldown_seconds: int = 5  # min seconds between manual admin refreshes

    def recalculate_destination_pressure(
        self,
        destination_id: str,
        target_date_str: Optional[str] = None,
        force_provider_refresh: bool = False
    ) -> DestinationLiveConditions:
        """
        Recalculates dynamic pressure for a destination using:
        - Weather impact (M7C)
        - Traffic impact (M7C)
        - Event pressure (M7B)
        - Holiday pressure (M7B)
        - First-party demand telemetry (M7A)
        - Historical footfall & accommodation occupancy
        """
        dest_clean = destination_id.lower().strip()
        dest_cfg = DESTINATION_CONFIG.get(dest_clean, DESTINATION_CONFIG["kalimpong"])
        now = datetime.utcnow()

        is_future_date = False
        target_date_obj = now.date()
        if target_date_str:
            try:
                target_date_obj = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                is_future_date = (target_date_obj > now.date())
            except ValueError:
                pass

        # 1. Weather Signal
        if is_future_date:
            condition_type = "FORECAST CONDITIONS"
            forecasts = weather_service.get_forecast(dest_clean, days=7)
            matching_obs = next(
                (f for f in forecasts if f.forecast_for == target_date_str),
                forecasts[0] if forecasts else weather_service.get_weather(dest_clean)
            )
            weather_obs = matching_obs
        else:
            condition_type = "CURRENT CONDITIONS"
            weather_obs = weather_service.get_weather(dest_clean, force_refresh=force_provider_refresh)

        weather_sig = weather_service.calculate_weather_impact(weather_obs)

        # 2. Traffic Signal (For future dates, traffic is strictly NOT assumed)
        traffic_sum = traffic_service.get_traffic(dest_clean, force_refresh=force_provider_refresh)
        traffic_sig = traffic_service.calculate_traffic_impact(traffic_sum)
        if is_future_date:
            # Future dates do not pretend real-time traffic is known
            traffic_sig.traffic_impact_score = 30.0  # nominal historical baseline
            traffic_sig.traffic_status = "NORMAL"
            traffic_sig.impact_description = "Nominal historical baseline; real-time traffic telemetry not applicable to future dates."

        # 3. Events & Holidays Signals (M7B)
        event_press = float(events_engine.calculate_event_pressure(dest_clean, target_date_obj).get("score", 10.0))
        holiday_press = float(holiday_engine.calculate_holiday_pressure(target_date_obj).get("score", 15.0))

        # 4. First-Party Demand Signal (M7A)
        try:
            demand_metrics = demand_aggregation_service.get_destination_demand(dest_clean)
            fp_demand_score = float(min(100.0, max(0.0, demand_metrics.availability_pressure)))
        except Exception:
            fp_demand_score = 45.0

        # 5. Base Footfall & Accommodation
        hist_footfall = dest_cfg["baseline_footfall"]
        acc_occupancy = dest_cfg["occupancy_base"]

        # 6. Combined Deterministic Normalization
        # Weights:
        # - Historical Footfall: 0.20
        # - Accommodation Occupancy: 0.15
        # - First-Party Demand: 0.15
        # - Traffic Pressure: 0.15 (or 0.05 on future dates)
        # - Event Pressure: 0.15
        # - Holiday Pressure: 0.10
        # - Weather Impact: 0.10
        if is_future_date:
            w_hist = 0.25
            w_occ = 0.20
            w_fp = 0.15
            w_traf = 0.05
            w_evt = 0.15
            w_hol = 0.10
            w_wth = 0.10
        else:
            w_hist = 0.20
            w_occ = 0.15
            w_fp = 0.15
            w_traf = 0.15
            w_evt = 0.15
            w_hol = 0.10
            w_wth = 0.10

        traffic_score = traffic_sig.traffic_impact_score
        # Weather impact score is mapped from [-1.0, 1.0] to [0, 100]
        # Pleasant weather (+0.2) -> 60. Moderate mist (-0.2) -> 40. Severe storm (-1.0) -> 0.
        weather_score = max(0.0, min(100.0, 50.0 + (weather_sig.weather_impact * 50.0)))

        composite_score = (
            (hist_footfall * w_hist) +
            (acc_occupancy * w_occ) +
            (fp_demand_score * w_fp) +
            (traffic_score * w_traf) +
            (event_press * w_evt) +
            (holiday_press * w_hol) +
            (weather_score * w_wth)
        )

        final_score = round(min(100.0, max(0.0, composite_score)), 1)
        level = classify_pressure_level(final_score)

        # Access status strictly from corridor traffic & severe weather alerts
        access_status = traffic_sum.access_status
        if weather_obs.severe_weather and "warning" in weather_obs.severe_weather.lower() and access_status == "OPEN":
            access_status = "CAUTION"

        # 7. Identify Top Drivers for Explainability
        drivers: List[PressureDriver] = [
            PressureDriver(
                signal="historical_footfall",
                impact=round(hist_footfall * w_hist, 1),
                description=f"Seasonal historical footfall baseline for {dest_cfg['name']}."
            ),
            PressureDriver(
                signal="occupancy",
                impact=round(acc_occupancy * w_occ, 1),
                description=f"Local accommodation and homestay occupancy level ({acc_occupancy:.0f}%)."
            ),
            PressureDriver(
                signal="demand",
                impact=round(fp_demand_score * w_fp, 1),
                description="Traveler search intent and booking inquiries in Yatri Setu Network."
            ),
            PressureDriver(
                signal="traffic",
                impact=round(traffic_score * w_traf, 1),
                description=f"Corridor travel time status ({traffic_sig.traffic_status}) on {traffic_sig.bottleneck_corridor or 'access routes'}."
            )
        ]

        if event_press > 20:
            drivers.append(PressureDriver(
                signal="event",
                impact=round(event_press * w_evt, 1),
                description="Active festival / carnival schedule creating localized gathering pressure."
            ))

        if holiday_press > 30:
            drivers.append(PressureDriver(
                signal="holiday",
                impact=round(holiday_press * w_hol, 1),
                description="Holiday or weekend cluster contributing to regional travel flow."
            ))

        if abs(weather_sig.weather_impact) > 0.05:
            drivers.append(PressureDriver(
                signal="weather",
                impact=round((weather_score - 50.0) * w_wth, 1),
                description=f"Mountain weather condition ({weather_obs.weather_condition}) influencing outdoor movement."
            ))

        # Sort drivers by absolute impact descending
        drivers.sort(key=lambda d: abs(d.impact), reverse=True)
        top_drivers = drivers[:4]

        # 8. Snapshot for "Why Pressure Changed"
        current_readings = {
            "score": final_score,
            "holiday": holiday_press * w_hol,
            "event": event_press * w_evt,
            "traffic": traffic_score * w_traf,
            "weather": weather_score * w_wth,
            "demand": fp_demand_score * w_fp,
            "refreshed_at": now
        }

        # Calculate pressure change if previous snapshot exists
        prev = self._current_snapshots.get(dest_clean)
        change_summary: Optional[PressureChangeSummary] = None

        if prev:
            score_delta = round(final_score - prev["score"], 1)
            change_drivers: List[PressureChangeDriver] = [
                PressureChangeDriver(
                    signal="holiday",
                    delta=round(current_readings["holiday"] - prev["holiday"], 1),
                    description="Holiday period influx variation"
                ),
                PressureChangeDriver(
                    signal="event",
                    delta=round(current_readings["event"] - prev["event"], 1),
                    description="Regional festival activity change"
                ),
                PressureChangeDriver(
                    signal="traffic",
                    delta=round(current_readings["traffic"] - prev["traffic"], 1),
                    description="Corridor travel-time anomaly adjustment"
                ),
                PressureChangeDriver(
                    signal="weather",
                    delta=round(current_readings["weather"] - prev["weather"], 1),
                    description="Weather suitability shift"
                ),
                PressureChangeDriver(
                    signal="demand",
                    delta=round(current_readings["demand"] - prev["demand"], 1),
                    description="First-party traveler intent shift"
                )
            ]
            # Filter non-zero drivers
            change_drivers = [d for d in change_drivers if abs(d.delta) >= 0.1]
            change_drivers.sort(key=lambda d: abs(d.delta), reverse=True)

            change_summary = PressureChangeSummary(
                destination_id=dest_clean,
                pressure_delta=score_delta,
                previous_score=prev["score"],
                current_score=final_score,
                drivers=change_drivers[:4],
                previous_refresh_at=prev["refreshed_at"],
                current_refresh_at=now
            )
            self._previous_snapshots[dest_clean] = prev

        self._current_snapshots[dest_clean] = current_readings

        # 9. Provenance Determination
        weather_mode = weather_obs.provider_mode
        traffic_mode = traffic_sum.provider_mode
        if weather_mode == "REAL" and traffic_mode == "REAL":
            provenance = "REAL — LIVE METEOROLOGICAL & CORRIDOR FEEDS"
            quality = "HIGH"
        elif weather_mode == "REAL" or traffic_mode == "REAL":
            provenance = "MIXED — REAL & DEMO CORRIDOR TELEMETRY"
            quality = "HIGH"
        elif weather_obs.cache_status == "STALE" or traffic_sum.cache_status == "STALE":
            provenance = "CACHED — TELEMETRY WITH GRACEFUL FALLBACK"
            quality = "MEDIUM"
        else:
            provenance = "DEMO — SYNTHETIC HIMALAYAN TELEMETRY"
            quality = "HIGH"

        return DestinationLiveConditions(
            destination_id=dest_clean,
            destination_name=dest_cfg["name"],
            condition_type=condition_type,
            pressure_score=final_score,
            pressure_level=level,
            access_status=access_status,
            weather=weather_obs,
            traffic=traffic_sum,
            weather_impact=weather_sig,
            traffic_impact=traffic_sig,
            event_pressure=round(event_press, 1),
            holiday_pressure=round(holiday_press, 1),
            first_party_demand=round(fp_demand_score, 1),
            top_drivers=top_drivers,
            pressure_change=change_summary,
            provenance=provenance,
            data_quality=quality,
            refreshed_at=now
        )

    def refresh_all_destinations(self, force: bool = False) -> Dict[str, DestinationLiveConditions]:
        """Refreshes live conditions and pressure for all destinations across the regional circuit."""
        results: Dict[str, DestinationLiveConditions] = {}
        for dest_id in ALL_DESTINATIONS:
            results[dest_id] = self.recalculate_destination_pressure(
                dest_id,
                force_provider_refresh=force
            )
        self._last_refresh_time = datetime.utcnow()
        return results

    def get_last_refresh_time(self) -> Optional[datetime]:
        return self._last_refresh_time


# Global Singleton Instance
pressure_refresh_service = PressureRefreshService()
