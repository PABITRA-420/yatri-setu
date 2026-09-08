"""
Data source providers for Yatri Setu Destination Pressure Intelligence Layer.
All 8 signals are abstracted through BaseDataSourceProvider with MOCK providers for local MVP.
"""
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading
from app.services.data_sources.tourism_data import tourism_data_provider, MockTourismDataProvider
from app.services.data_sources.accommodation_data import accommodation_data_provider, MockAccommodationDataProvider
from app.services.data_sources.booking_demand import booking_demand_provider, MockBookingDemandProvider
from app.services.data_sources.search_demand import search_demand_provider, MockSearchDemandProvider
from app.services.data_sources.events_data import event_data_provider, MockEventDataProvider
from app.services.data_sources.holiday_data import holiday_data_provider, MockHolidayDataProvider
from app.services.data_sources.traffic_data import traffic_data_provider, MockTrafficDataProvider
from app.services.data_sources.weather_data import weather_data_provider, MockWeatherDataProvider

__all__ = [
    "BaseDataSourceProvider",
    "DataSourceReading",
    "tourism_data_provider",
    "MockTourismDataProvider",
    "accommodation_data_provider",
    "MockAccommodationDataProvider",
    "booking_demand_provider",
    "MockBookingDemandProvider",
    "search_demand_provider",
    "MockSearchDemandProvider",
    "event_data_provider",
    "MockEventDataProvider",
    "holiday_data_provider",
    "MockHolidayDataProvider",
    "traffic_data_provider",
    "MockTrafficDataProvider",
    "weather_data_provider",
    "MockWeatherDataProvider",
]
