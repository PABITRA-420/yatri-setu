"""
Holiday Data Provider for Yatri Setu.
Provides normalized holiday pressure readings (0-100) combining
national holidays, state gazetted festivals, and long-weekend tourism spikes.
"""
from datetime import datetime, date
from typing import Optional
from app.services.data_sources.base import BaseDataSourceProvider, DataSourceReading
from app.services.holiday_engine import holiday_engine


class MockHolidayDataProvider(BaseDataSourceProvider):
    """
    Simulates calendar surge effects based on national holidays,
    regional Himalayan festivals, and extended weekend bridges.
    """
    PROVIDER_TYPE = "MOCK"

    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        target_date = date.today()
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        res = holiday_engine.calculate_holiday_pressure(target_date)
        score = res["score"]
        h_name = res.get("holiday_name")
        status = res.get("weekend_status", "Regular day")

        notes = f"{status}"
        if h_name:
            notes += f" ({h_name})"

        return DataSourceReading(
            value=score,
            available=True,
            source="MOCK_NATIONAL_CALENDAR_ENGINE",
            confidence=0.96,
            raw_value=score,
            unit="calendar_surge_index",
            provider_mode="MOCK",
            data_quality="HIGH",
            signal_type="HOLIDAY",
            notes=notes
        )


holiday_data_provider = MockHolidayDataProvider()
