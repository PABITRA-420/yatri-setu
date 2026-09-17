from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class WeatherForecast(BaseModel):
    destination_id: str
    destination_name: str
    temperature_range_c: str
    temp_min_c: int
    temp_max_c: int
    condition: str
    precipitation_chance_percent: int
    rain_expected: bool
    mountain_visibility_score: int = Field(..., ge=0, le=100)
    advisory: str
    best_hours_for_outdoors: str
    is_demo_forecast: bool = True
    provider_source: str = "Yatri Setu Himalayan Meteorological Simulator"
    humidity: Optional[int] = None
    precipitation_mm: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    observed_at: Optional[datetime] = None
    cache_status: Optional[str] = None
    provenance_label: Optional[str] = None
    provider_mode: Optional[str] = None

# Deterministic realistic regional weather profiles (preserved for legacy tests and mock mode)
DESTINATION_WEATHER: Dict[str, Dict[str, Any]] = {
    "darjeeling": {
        "destination_name": "Darjeeling",
        "temperature_range_c": "11°C - 17°C",
        "temp_min_c": 11,
        "temp_max_c": 17,
        "condition": "Partly Cloudy with Afternoon Mist",
        "precipitation_chance_percent": 35,
        "rain_expected": False,
        "mountain_visibility_score": 82,
        "advisory": "Crisp morning views of Kanchenjunga from 5:30 AM to 8:30 AM. Valley fog gathers after 2 PM.",
        "best_hours_for_outdoors": "06:00 AM - 12:30 PM"
    },
    "kalimpong": {
        "destination_name": "Kalimpong",
        "temperature_range_c": "14°C - 22°C",
        "temp_min_c": 14,
        "temp_max_c": 22,
        "condition": "Mild Sun & Gentle Mountain Breezes",
        "precipitation_chance_percent": 20,
        "rain_expected": False,
        "mountain_visibility_score": 90,
        "advisory": "Clear skies across Teesta gorge with excellent visibility for Deolo paragliding and orchid visits.",
        "best_hours_for_outdoors": "08:00 AM - 04:30 PM"
    },
    "lava": {
        "destination_name": "Lava",
        "temperature_range_c": "9°C - 15°C",
        "temp_min_c": 9,
        "temp_max_c": 15,
        "condition": "Misty Pine Forests with Brief Mountain Drizzle",
        "precipitation_chance_percent": 65,
        "rain_expected": True,
        "mountain_visibility_score": 68,
        "advisory": "Light afternoon drizzle expected in Neora Valley. Outdoor forest treks best scheduled for early morning; covered monastery visits recommended in afternoon.",
        "best_hours_for_outdoors": "06:30 AM - 11:30 AM"
    },
    "lolegaon": {
        "destination_name": "Lolegaon",
        "temperature_range_c": "12°C - 18°C",
        "temp_min_c": 12,
        "temp_max_c": 18,
        "condition": "Cool Forest Canopy with Occasional Cloud Cover",
        "precipitation_chance_percent": 30,
        "rain_expected": False,
        "mountain_visibility_score": 75,
        "advisory": "Comfortable trekking weather for canopy walkway with mild humidity under oak cover.",
        "best_hours_for_outdoors": "08:00 AM - 02:00 PM"
    },
    "rishop": {
        "destination_name": "Rishop",
        "temperature_range_c": "7°C - 13°C",
        "temp_min_c": 7,
        "temp_max_c": 13,
        "condition": "Crystal Clear Mountain Air & Cold Nights",
        "precipitation_chance_percent": 10,
        "rain_expected": False,
        "mountain_visibility_score": 96,
        "advisory": "Exceptional panoramic sunrise visibility over Mt. Kanchenjunga. Heavy woolens required for evening fireside stargazing.",
        "best_hours_for_outdoors": "05:15 AM - 03:00 PM"
    },
    "mirik": {
        "destination_name": "Mirik",
        "temperature_range_c": "13°C - 20°C",
        "temp_min_c": 13,
        "temp_max_c": 20,
        "condition": "Pleasant Lake Breezes with Warm Sunshine",
        "precipitation_chance_percent": 15,
        "rain_expected": False,
        "mountain_visibility_score": 85,
        "advisory": "Calm water conditions ideal for boating on Sumendu Lake and walking through orange orchards.",
        "best_hours_for_outdoors": "09:00 AM - 04:00 PM"
    }
}

class BaseWeatherProvider:
    def get_weather(self, destination_id: str, date_range: Optional[str] = None) -> WeatherForecast:
        raise NotImplementedError

class MockWeatherProvider(BaseWeatherProvider):
    def get_weather(self, destination_id: str, date_range: Optional[str] = None) -> WeatherForecast:
        norm_id = destination_id.lower().strip()
        data = DESTINATION_WEATHER.get(norm_id, DESTINATION_WEATHER["kalimpong"])
        return WeatherForecast(
            destination_id=norm_id,
            destination_name=data["destination_name"],
            temperature_range_c=data["temperature_range_c"],
            temp_min_c=data["temp_min_c"],
            temp_max_c=data["temp_max_c"],
            condition=data["condition"],
            precipitation_chance_percent=data["precipitation_chance_percent"],
            rain_expected=data["rain_expected"],
            mountain_visibility_score=data["mountain_visibility_score"],
            advisory=data["advisory"],
            best_hours_for_outdoors=data["best_hours_for_outdoors"],
            is_demo_forecast=True,
            provider_source="Yatri Setu Himalayan Meteorological Simulator",
            provenance_label="DEMO MODE — SYNTHETIC DATA",
            provider_mode="DEMO"
        )


class CanonicalWeatherProvider(BaseWeatherProvider):
    """
    Connects tourist-facing weather calls directly to the unified WeatherService (M7C),
    ensuring identical real OpenWeather observations, destination-specific coordinates,
    shared TTL cache, and explicit provenance.
    """
    def get_weather(self, destination_id: str, date_range: Optional[str] = None) -> WeatherForecast:
        from app.services.weather.service import weather_service
        obs = weather_service.get_weather(destination_id)

        temp_min = int(round(obs.temp_min_c))
        temp_max = int(round(obs.temp_max_c))
        temp_range = f"{temp_min}°C - {temp_max}°C"
        if obs.destination_id in DESTINATION_WEATHER and obs.provider_mode == "DEMO":
            rain_expected = DESTINATION_WEATHER[obs.destination_id].get("rain_expected", False)
            visibility_score = DESTINATION_WEATHER[obs.destination_id].get("mountain_visibility_score", 85)
        else:
            rain_expected = (obs.precipitation_mm > 0.5 or obs.precipitation_probability >= 50)
            base_score = min(100.0, (obs.visibility_km / 10.0) * 80.0)
            if rain_expected:
                base_score -= 25.0
            visibility_score = int(max(10, min(100, round(base_score))))

        is_demo = (obs.provider_mode != "REAL")

        if obs.provider_mode == "REAL":
            if obs.cache_status == "CACHED":
                provider_source = "OpenWeatherMap (Cached)"
                prov_label = "CACHED — OPENWEATHER"
            elif obs.cache_status == "STALE":
                provider_source = "OpenWeatherMap (Stale)"
                prov_label = "MIXED — STALE TELEMETRY FALLBACK"
            else:
                provider_source = "OpenWeatherMap"
                prov_label = "REAL — OPENWEATHER"
        else:
            provider_source = "Yatri Setu Himalayan Meteorological Simulator"
            prov_label = "DEMO MODE — SYNTHETIC DATA"

        return WeatherForecast(
            destination_id=obs.destination_id,
            destination_name=obs.destination_name,
            temperature_range_c=temp_range,
            temp_min_c=temp_min,
            temp_max_c=temp_max,
            condition=obs.weather_condition,
            precipitation_chance_percent=obs.precipitation_probability,
            rain_expected=rain_expected,
            mountain_visibility_score=visibility_score,
            advisory=obs.advisory,
            best_hours_for_outdoors=obs.best_hours_for_outdoors,
            is_demo_forecast=is_demo,
            provider_source=provider_source,
            humidity=obs.humidity,
            precipitation_mm=obs.precipitation_mm,
            wind_speed_kmh=obs.wind_speed_kmh,
            observed_at=obs.observed_at,
            cache_status=obs.cache_status,
            provenance_label=prov_label,
            provider_mode=obs.provider_mode
        )


# Factory singleton: defaults to CanonicalWeatherProvider wired to unified WeatherService
weather_provider: BaseWeatherProvider = CanonicalWeatherProvider()

def get_destination_weather(destination_id: str, date_range: Optional[str] = None) -> WeatherForecast:
    return weather_provider.get_weather(destination_id, date_range)
