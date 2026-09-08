"""
Event Data Source Provider for Yatri Setu.
Provides normalized event pressure (0-100) based on local festivals,
carnivals, sporting events, and cultural gatherings.
"""
from datetime import datetime, date
from typing import Optional
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading
from app.services.events_engine import events_engine


class MockEventDataProvider(BaseDataSourceProvider):
    """
    Simulates event intelligence for Himalayan destinations.
    Connects to events_engine for regional schedule lookup.
    """
    PROVIDER_TYPE = "MOCK"

    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        target_date = None
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                target_date = date.today()
        else:
            target_date = date.today()

        pressure_info = events_engine.calculate_event_pressure(destination_id, target_date)
        score = pressure_info["score"]
        events_active = len(pressure_info["active_events"])

        notes = pressure_info["summary"]
        if events_active > 0:
            notes += f" ({events_active} major event(s))"

        return DataSourceReading(
            value=score,
            available=True,
            source="MOCK_REGIONAL_EVENT_CALENDAR",
            confidence=0.92,
            raw_value=float(events_active),
            unit="active_events",
            provider_mode="MOCK",
            data_quality="HIGH",
            signal_type="EVENT",
            notes=notes
        )


event_data_provider = MockEventDataProvider()
