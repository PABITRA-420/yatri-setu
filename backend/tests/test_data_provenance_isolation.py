"""
Tests for Data Provenance Isolation, Classification, and Transparency.

Verifies:
1. Synthetic data remains available for unit tests and local development.
2. Production paths never label synthetic/demo data as LIVE or REAL.
3. Provider failure produces CACHED (stale) or UNAVAILABLE state without fabricating new values.
4. Provenance and data status are strictly preserved across models and API endpoints.
5. Legitimate fallbacks remain functional without arbitrary multiplier formulas.
"""
import pytest
from unittest.mock import patch, MagicMock

from app.services.data_sources.base import (
    DataSourceReading, BaseDataSourceProvider, VALID_PROVIDER_MODES
)
from app.services.data_sources.tourism_data import MockTourismDataProvider
from app.services.data_sources.accommodation_data import MockAccommodationDataProvider
from app.services.data_sources.search_demand import MockSearchDemandProvider
from app.services.data_sources.events_data import MockEventDataProvider
from app.services.data_sources.holiday_data import MockHolidayDataProvider
from app.services.weather.service import WeatherService
from app.services.weather.provider import DemoWeatherProvider, UnavailableWeatherProvider
from app.services.traffic.service import TrafficService
from app.services.traffic.provider import DemoTrafficProvider, UnavailableTrafficProvider
from app.services.alternative_engine import get_alternative_destinations
from app.services.conversion.funnel_service import conversion_funnel_service
from app.services.demand_aggregation_service import demand_aggregation_service
from app.data.historical_dataset import HistoricalObservation, DESTINATIONS


class TestSyntheticDataAvailabilityForTests:
    """Verifies all test fixtures, mock providers, and historical generators remain fully available."""

    def test_mock_tourism_data_provider(self):
        provider = MockTourismDataProvider()
        reading = provider.get_reading("darjeeling")
        assert reading.available is True
        assert reading.provider_mode == "MOCK"
        assert "not live state tourism data" in reading.notes.lower()
        assert reading.value == 92.0

    def test_mock_accommodation_provider(self):
        provider = MockAccommodationDataProvider()
        reading = provider.get_reading("kalimpong")
        assert reading.available is True
        assert reading.provider_mode == "MOCK"
        assert reading.value > 0

    def test_mock_search_demand_provider(self):
        provider = MockSearchDemandProvider()
        reading = provider.get_reading("mirik")
        assert reading.available is True
        assert reading.provider_mode == "MOCK"
        assert "MOCK_SEARCH_DEMAND" in reading.source

    def test_demo_weather_and_traffic_providers(self):
        demo_w = DemoWeatherProvider()
        obs = demo_w.fetch_current("darjeeling")
        assert obs.provider_mode == "DEMO"
        assert "DEMO" in obs.provenance_label

        demo_t = DemoTrafficProvider()
        summary = demo_t.fetch_traffic("darjeeling")
        assert summary.provider_mode == "DEMO"
        assert "DEMO" in summary.provenance_label

    def test_historical_dataset_generator(self):
        """Historical observations must remain available but labeled SYNTHETIC_GENERATOR."""
        from datetime import date
        from app.data.historical_dataset import generate_historical_dataset
        dataset = generate_historical_dataset(start_date=date(2023, 1, 1), end_date=date(2023, 1, 2))
        assert len(dataset) > 0
        obs = dataset[0]
        assert obs.source == "SYNTHETIC_GENERATOR"
        assert obs.destination_id in ("darjeeling", "kalimpong", "lava", "lolegaon", "rishop", "mirik")
        assert obs.date == "2023-01-01"


class TestNoSyntheticDataSilentlyLabeledReal:
    """Verifies that production paths NEVER label synthetic data as REAL or LIVE."""

    def test_data_source_reading_valid_modes(self):
        reading = DataSourceReading(
            value=50.0,
            available=False,
            source="MOCK",
            provider_mode="UNAVAILABLE"
        )
        assert reading.provider_mode == "UNAVAILABLE"
        assert reading.provider_mode in VALID_PROVIDER_MODES

    def test_demo_weather_never_claims_real(self):
        svc = WeatherService()
        svc.set_provider(DemoWeatherProvider())
        obs = svc.get_weather("darjeeling")
        assert obs.provider_mode != "REAL"
        assert "REAL — OPENWEATHER" not in obs.provenance_label
        assert "DEMO" in obs.provenance_label or "SYNTHETIC" in obs.provenance_label

    def test_demo_traffic_never_claims_real(self):
        svc = TrafficService(provider=DemoTrafficProvider())
        summary = svc.get_traffic("darjeeling")
        assert summary.provider_mode != "REAL"
        assert "REAL — TOMTOM" not in summary.provenance_label
        assert "DEMO" in summary.provenance_label or "SYNTHETIC" in summary.provenance_label


class TestProviderFailureProducesCachedOrUnavailable:
    """Verifies graceful degradation without manufacturing fake numerical values."""

    def test_weather_unavailable_provider(self):
        svc = WeatherService()
        svc.set_provider(UnavailableWeatherProvider())
        obs = svc.get_weather("kalimpong")
        assert obs.provider_mode == "UNAVAILABLE"

    def test_traffic_unavailable_provider(self):
        svc = TrafficService(provider=UnavailableTrafficProvider())
        summary = svc.get_traffic("kalimpong")
        assert summary.provider_mode in ("UNAVAILABLE", "DEMO")
        assert summary.access_status in ("CAUTION", "OPEN", "UNKNOWN")

    def test_weather_stale_cache_behavior(self):
        import time
        svc = WeatherService(ttl_seconds=1)
        demo = DemoWeatherProvider()
        svc.set_provider(demo)
        obs1 = svc.get_weather("darjeeling")
        assert obs1 is not None

        # Wait for TTL to expire so entry becomes stale
        time.sleep(1.1)

        # Simulate provider failure on subsequent call with existing stale cache
        failing_provider = MagicMock()
        failing_provider.fetch_current.side_effect = RuntimeError("OpenWeather 503 Service Unavailable")
        svc.set_provider(failing_provider)

        obs2 = svc.get_weather("darjeeling")
        assert obs2.cache_status == "STALE"
        assert obs2.data_quality == "DEGRADED"


class TestAlternativeRecommendationProvenance:
    """Verifies alternative recommendation calibration is explicitly labeled."""

    def test_similarity_provenance_is_classified(self):
        res = get_alternative_destinations("darjeeling")
        assert len(res.alternatives) > 0
        top = res.alternatives[0]
        # Must have explicit similarity provenance (benchmark vs measured)
        assert hasattr(top, "similarity_provenance")
        assert top.similarity_provenance == "DEMO_CALIBRATION_BENCHMARK"
        # Must have explicit distance provenance
        assert top.distance_provenance in ("OSRM_ROAD_DISTANCE", "HAVERSINE_GEOGRAPHIC_ESTIMATE")


class TestConversionFunnelNoArbitraryMultipliers:
    """Verifies conversion funnel uses genuine event observations rather than fabricated multiplier formulas."""

    def test_funnel_counts_match_genuine_demand_events(self):
        funnel = conversion_funnel_service.get_funnel()
        assert len(funnel) == 6
        
        stages = {s.stage: s.count for s in funnel}
        raw_events = demand_aggregation_service._events

        expected_searches = len([e for e in raw_events if e.get("event_type") == "search"])
        expected_views = len([e for e in raw_events if e.get("event_type") == "alternative_viewed"])

        assert stages["SEARCH"] == expected_searches
        assert stages["ALTERNATIVE_VIEW"] == expected_views
