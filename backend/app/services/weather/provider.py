"""
Weather Providers Implementation for Yatri Setu (Milestone 7C).
Supports Demo/Synthetic, Real OpenWeather, and Unavailable fallback providers.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
import httpx

from app.core.config import settings
from app.services.weather.base import BaseWeatherProvider
from app.services.weather.schemas import WeatherObservation

logger = logging.getLogger(__name__)

# Destination coordinates for meteorological queries
DESTINATION_COORDINATES: Dict[str, Tuple[float, float]] = {
    "darjeeling": (27.0410, 88.2663),
    "kalimpong": (27.0594, 88.4695),
    "lava": (27.0864, 88.6603),
    "lolegaon": (27.0142, 88.5583),
    "rishop": (27.1065, 88.6496),
    "mirik": (26.9011, 88.1755),
}

# Rich regional baseline profiles
DEMO_WEATHER_PROFILES: Dict[str, Dict[str, Any]] = {
    "darjeeling": {
        "name": "Darjeeling",
        "temp_c": 14.5,
        "temp_min": 11.0,
        "temp_max": 17.5,
        "condition": "Partly Cloudy with Valley Mist",
        "precip_prob": 35,
        "precip_mm": 2.5,
        "humidity": 68,
        "wind_kmh": 12.0,
        "visibility_km": 12.0,
        "severe_weather": None,
        "advisory": "Crisp morning views of Mt. Kanchenjunga from Tiger Hill (05:30 - 08:30). Ridge mist develops after 2 PM.",
        "best_hours": "06:00 AM - 12:30 PM"
    },
    "kalimpong": {
        "name": "Kalimpong",
        "temp_c": 18.2,
        "temp_min": 14.0,
        "temp_max": 22.0,
        "condition": "Mild Sunshine & Gentle Mountain Breeze",
        "precip_prob": 20,
        "precip_mm": 0.5,
        "humidity": 58,
        "wind_kmh": 9.0,
        "visibility_km": 18.0,
        "severe_weather": None,
        "advisory": "Clear skies over Teesta Gorge. Excellent visibility for Deolo paragliding and orchid nursery visits.",
        "best_hours": "08:00 AM - 04:30 PM"
    },
    "lava": {
        "name": "Lava",
        "temp_c": 12.0,
        "temp_min": 9.0,
        "temp_max": 15.0,
        "condition": "Misty Pine Forests with Intermittent Drizzle",
        "precip_prob": 65,
        "precip_mm": 8.0,
        "humidity": 82,
        "wind_kmh": 14.0,
        "visibility_km": 6.5,
        "severe_weather": None,
        "advisory": "Light afternoon drizzle expected across Neora Valley. Forest trails best walked before noon; monastery tours recommended later.",
        "best_hours": "06:30 AM - 11:30 AM"
    },
    "lolegaon": {
        "name": "Lolegaon",
        "temp_c": 15.0,
        "temp_min": 12.0,
        "temp_max": 18.0,
        "condition": "Cool Forest Canopy with Shifting Clouds",
        "precip_prob": 30,
        "precip_mm": 1.5,
        "humidity": 70,
        "wind_kmh": 8.0,
        "visibility_km": 14.0,
        "severe_weather": None,
        "advisory": "Pleasant trekking temperatures for heritage canopy walkway under moss-covered oak trees.",
        "best_hours": "08:00 AM - 02:00 PM"
    },
    "rishop": {
        "name": "Rishop",
        "temp_c": 10.5,
        "temp_min": 7.0,
        "temp_max": 13.5,
        "condition": "Crystal Clear High Alpine Air",
        "precip_prob": 10,
        "precip_mm": 0.0,
        "humidity": 50,
        "wind_kmh": 11.0,
        "visibility_km": 25.0,
        "severe_weather": None,
        "advisory": "Spectacular 360-degree panoramic sunrise visibility over snowy peaks. Heavy woolens required for evening firesides.",
        "best_hours": "05:15 AM - 03:00 PM"
    },
    "mirik": {
        "name": "Mirik",
        "temp_c": 16.8,
        "temp_min": 13.0,
        "temp_max": 20.5,
        "condition": "Pleasant Lake Breeze & Warm Sunshine",
        "precip_prob": 15,
        "precip_mm": 0.2,
        "humidity": 62,
        "wind_kmh": 10.0,
        "visibility_km": 16.0,
        "severe_weather": None,
        "advisory": "Calm water conditions ideal for boating on Sumendu Lake and leisurely walks through orange orchards.",
        "best_hours": "09:00 AM - 04:00 PM"
    }
}


class DemoWeatherProvider(BaseWeatherProvider):
    """
    High-fidelity deterministic simulator for Himalayan hill station weather.
    Provides realistic diurnal variations and multi-day forecasts.
    """

    def is_available(self) -> bool:
        return True

    def get_provider_mode(self) -> str:
        return "DEMO"

    def fetch_current(self, destination_id: str) -> WeatherObservation:
        dest_clean = destination_id.lower().strip()
        data = DEMO_WEATHER_PROFILES.get(dest_clean, DEMO_WEATHER_PROFILES["kalimpong"])
        now = datetime.utcnow()

        return WeatherObservation(
            destination_id=dest_clean,
            destination_name=data["name"],
            observed_at=now,
            forecast_for=None,
            temperature_c=data["temp_c"],
            temp_min_c=data["temp_min"],
            temp_max_c=data["temp_max"],
            precipitation_probability=data["precip_prob"],
            precipitation_mm=data["precip_mm"],
            humidity=data["humidity"],
            wind_speed_kmh=data["wind_kmh"],
            weather_condition=data["condition"],
            severe_weather=data["severe_weather"],
            visibility_km=data["visibility_km"],
            advisory=data["advisory"],
            best_hours_for_outdoors=data["best_hours"],
            source="DEMO_HIMALAYAN_MET_SIMULATOR",
            provider_mode="DEMO",
            provenance_label="DEMO MODE — SYNTHETIC DATA",
            confidence=0.88,
            data_quality="HIGH",
            fetched_at=now,
            cache_status="LIVE"
        )

    def fetch_forecast(self, destination_id: str, days: int = 7) -> List[WeatherObservation]:
        dest_clean = destination_id.lower().strip()
        base = self.fetch_current(dest_clean)
        now = datetime.utcnow()

        forecasts: List[WeatherObservation] = []
        for i in range(1, days + 1):
            f_date = (now + timedelta(days=i)).strftime("%Y-%m-%d")
            # Slight diurnal / seasonal drift per day
            temp_drift = round((((i * 3) % 5) - 2) * 0.7, 1)
            rain_mod = 10 if (i % 3 == 0) else -5

            obs = WeatherObservation(
                destination_id=dest_clean,
                destination_name=base.destination_name,
                observed_at=now,
                forecast_for=f_date,
                temperature_c=round(base.temperature_c + temp_drift, 1),
                temp_min_c=round(base.temp_min_c + temp_drift, 1),
                temp_max_c=round(base.temp_max_c + temp_drift, 1),
                precipitation_probability=max(5, min(95, base.precipitation_probability + rain_mod)),
                precipitation_mm=round(max(0.0, base.precipitation_mm + (rain_mod * 0.1)), 1),
                humidity=base.humidity,
                wind_speed_kmh=base.wind_speed_kmh,
                weather_condition=base.weather_condition,
                severe_weather=base.severe_weather,
                visibility_km=base.visibility_km,
                advisory=f"Forecast for {f_date}: {base.advisory}",
                best_hours_for_outdoors=base.best_hours_for_outdoors,
                source="DEMO_HIMALAYAN_MET_SIMULATOR",
                provider_mode="DEMO",
                provenance_label="DEMO MODE — SYNTHETIC DATA",
                confidence=max(0.60, round(base.confidence - (i * 0.04), 2)),
                data_quality="MEDIUM" if i > 3 else "HIGH",
                fetched_at=now,
                cache_status="LIVE"
            )
            forecasts.append(obs)

        return forecasts


class OpenWeatherProvider(BaseWeatherProvider):
    """
    Real OpenWeather API implementation with strict timeout and error handling.
    Only active when WEATHER_PROVIDER == 'openweather' and API key is set.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.WEATHER_API_KEY or settings.OPENWEATHER_API_KEY

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def get_provider_mode(self) -> str:
        return "REAL"

    def fetch_current(self, destination_id: str) -> WeatherObservation:
        dest_clean = destination_id.lower().strip()
        if not self.is_available():
            raise RuntimeError("OpenWeatherProvider API key is not configured")

        coords = DESTINATION_COORDINATES.get(dest_clean, (27.0594, 88.4695))
        lat, lon = coords
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
        )

        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    raise RuntimeError(f"OpenWeather API returned status {resp.status_code}: {resp.text}")

                data = resp.json()
                now = datetime.utcnow()
                temp = float(data.get("main", {}).get("temp", 16.0))
                temp_min = float(data.get("main", {}).get("temp_min", temp - 3.0))
                temp_max = float(data.get("main", {}).get("temp_max", temp + 3.0))
                humidity = int(data.get("main", {}).get("humidity", 60))
                wind_speed = float(data.get("wind", {}).get("speed", 3.0)) * 3.6  # m/s to km/h
                visibility = float(data.get("visibility", 10000)) / 1000.0  # meters to km

                weather_item = data.get("weather", [{}])[0]
                condition = weather_item.get("description", "Clear sky").title()
                condition_main = weather_item.get("main", "Clear").lower()

                # Precipitation estimation from rain dict if available
                rain_dict = data.get("rain", {})
                rain_1h = float(rain_dict.get("1h", 0.0))
                precip_prob = 80 if rain_1h > 0 else (40 if "cloud" in condition_main else 10)

                severe = None
                if "thunderstorm" in condition_main or wind_speed > 55.0 or rain_1h > 15.0:
                    severe = f"Severe Weather Alert: {condition} with high winds/rain in mountain corridor."

                return WeatherObservation(
                    destination_id=dest_clean,
                    destination_name=dest_clean.title(),
                    observed_at=now,
                    forecast_for=None,
                    temperature_c=temp,
                    temp_min_c=temp_min,
                    temp_max_c=temp_max,
                    precipitation_probability=precip_prob,
                    precipitation_mm=rain_1h,
                    humidity=humidity,
                    wind_speed_kmh=round(wind_speed, 1),
                    weather_condition=condition,
                    severe_weather=severe,
                    visibility_km=round(visibility, 1),
                    advisory=f"Live meteorological observation: {condition} at {temp:.1f}°C, wind {wind_speed:.1f} km/h.",
                    best_hours_for_outdoors="Morning to early afternoon",
                    source="OPENWEATHERMAP_LIVE",
                    provider_mode="REAL",
                    provenance_label="REAL — EXTERNAL PROVIDER",
                    confidence=0.95,
                    data_quality="HIGH",
                    fetched_at=now,
                    cache_status="LIVE"
                )
        except Exception as e:
            logger.warning(f"OpenWeatherProvider failed for {destination_id}: {e}")
            raise RuntimeError(f"OpenWeather API request failed: {e}") from e

    def fetch_forecast(self, destination_id: str, days: int = 7) -> List[WeatherObservation]:
        # Fallback to demo forecast generator or OpenWeather 5-day forecast endpoint
        demo = DemoWeatherProvider()
        return demo.fetch_forecast(destination_id, days)


class UnavailableWeatherProvider(BaseWeatherProvider):
    """Fallback provider when no live or demo provider is operational."""

    def is_available(self) -> bool:
        return False

    def get_provider_mode(self) -> str:
        return "UNAVAILABLE"

    def fetch_current(self, destination_id: str) -> WeatherObservation:
        dest_clean = destination_id.lower().strip()
        now = datetime.utcnow()
        return WeatherObservation(
            destination_id=dest_clean,
            destination_name=dest_clean.title(),
            observed_at=now,
            forecast_for=None,
            temperature_c=15.0,
            temp_min_c=12.0,
            temp_max_c=18.0,
            precipitation_probability=30,
            precipitation_mm=0.0,
            humidity=60,
            wind_speed_kmh=10.0,
            weather_condition="Weather Data Temporarily Unavailable",
            severe_weather=None,
            visibility_km=10.0,
            advisory="Weather telemetry is currently unavailable from external providers.",
            source="WEATHER_PROVIDER_UNAVAILABLE",
            provider_mode="UNAVAILABLE",
            provenance_label="UNAVAILABLE — SAFE FALLBACK",
            confidence=0.0,
            data_quality="UNKNOWN",
            fetched_at=now,
            cache_status="UNAVAILABLE"
        )

    def fetch_forecast(self, destination_id: str, days: int = 7) -> List[WeatherObservation]:
        obs = self.fetch_current(destination_id)
        now = datetime.utcnow()
        return [
            WeatherObservation(
                **{**obs.model_dump(), "forecast_for": (now + timedelta(days=i)).strftime("%Y-%m-%d")}
            )
            for i in range(1, days + 1)
        ]
