"""
Holiday & Calendar Intelligence Engine for Yatri Setu.
Tracks national holidays, regional Himalayan/West Bengal gazetted holidays,
long weekend clustering, and tourist travel spikes.
"""
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional, Dict, Tuple


@dataclass
class HolidayDefinition:
    name: str
    month: int
    day: int
    holiday_type: str  # "national", "regional", "cultural"
    impact_level: float  # 0.0 to 100.0 (impact on leisure travel)
    state: str = "ALL"  # "ALL" or "WB"


ANNUAL_HOLIDAYS: List[HolidayDefinition] = [
    HolidayDefinition("New Year's Day", 1, 1, "national", 75.0),
    HolidayDefinition("Netaji Subhash Chandra Bose Jayanti", 1, 23, "regional", 65.0, "WB"),
    HolidayDefinition("Republic Day", 1, 26, "national", 80.0),
    HolidayDefinition("Saraswati Puja", 2, 14, "regional", 70.0, "WB"),
    HolidayDefinition("Maha Shivratri", 3, 8, "cultural", 60.0),
    HolidayDefinition("Holi / Dol Jatra", 3, 25, "national", 85.0),
    HolidayDefinition("Good Friday", 3, 29, "national", 75.0),
    HolidayDefinition("Bhanu Jayanti (Gorkha Heritage)", 7, 13, "regional", 80.0, "WB"),
    HolidayDefinition("Independence Day", 8, 15, "national", 90.0),
    HolidayDefinition("Raksha Bandhan", 8, 19, "cultural", 55.0),
    HolidayDefinition("Janmashtami", 8, 26, "cultural", 55.0),
    HolidayDefinition("Mahatma Gandhi Jayanti", 10, 2, "national", 85.0),
    HolidayDefinition("Durga Puja (Maha Saptami)", 10, 10, "regional", 95.0, "WB"),
    HolidayDefinition("Durga Puja (Maha Ashtami/Navami)", 10, 11, "regional", 98.0, "WB"),
    HolidayDefinition("Vijaya Dashami / Dussehra", 10, 12, "national", 95.0),
    HolidayDefinition("Diwali / Kali Puja", 11, 1, "national", 95.0),
    HolidayDefinition("Bhai Dooj", 11, 3, "cultural", 70.0),
    HolidayDefinition("Guru Nanak Jayanti", 11, 15, "national", 65.0),
    HolidayDefinition("Christmas Day", 12, 25, "national", 92.0),
    HolidayDefinition("Year-End Festive Eve", 12, 31, "national", 95.0),
]


class HolidayEngine:
    """Evaluates holiday proximity, long weekends, and peak holiday travel surges."""

    def __init__(self, holidays: Optional[List[HolidayDefinition]] = None):
        self.holidays = holidays or ANNUAL_HOLIDAYS

    def get_holiday_on_date(self, target_date: date) -> Optional[HolidayDefinition]:
        """Check if target date is an exact holiday."""
        for h in self.holidays:
            if h.month == target_date.month and h.day == target_date.day:
                return h
        return None

    def detect_long_weekend(self, target_date: date) -> Tuple[bool, str]:
        """
        Check if target date is part of a 3+ day weekend.
        Friday holiday => Fri-Sat-Sun
        Monday holiday => Sat-Sun-Mon
        Thursday holiday => often taken as 4-day bridge
        Tuesday holiday => bridge weekend
        """
        weekday = target_date.weekday()  # Mon=0, Tue=1, ... Sun=6

        # Check today, yesterday, tomorrow, and ±2 days
        window_start = target_date - timedelta(days=2)
        window_end = target_date + timedelta(days=2)

        holidays_in_window = []
        curr = window_start
        while curr <= window_end:
            h = self.get_holiday_on_date(curr)
            if h:
                holidays_in_window.append((curr, h))
            curr += timedelta(days=1)

        # Direct weekend check
        is_weekend = weekday in (5, 6)

        for h_date, h in holidays_in_window:
            h_weekday = h_date.weekday()
            # If Friday holiday and today is Fri/Sat/Sun
            if h_weekday == 4 and weekday in (4, 5, 6):
                return True, f"Long weekend (Friday {h.name})"
            # If Monday holiday and today is Sat/Sun/Mon
            if h_weekday == 0 and weekday in (5, 6, 0):
                return True, f"Long weekend (Monday {h.name})"
            # If Thursday holiday bridge
            if h_weekday == 3 and weekday in (3, 4, 5, 6):
                return True, f"Extended weekend bridge ({h.name})"
            # If Tuesday holiday bridge
            if h_weekday == 1 and weekday in (5, 6, 0, 1):
                return True, f"Extended weekend bridge ({h.name})"

        if is_weekend:
            return False, "Standard weekend"
        return False, "Regular weekday"

    def calculate_holiday_pressure(self, target_date: Optional[date] = None) -> Dict:
        """
        Calculate composite holiday pressure (0-100) for a given date.
        Returns score, holiday details, long weekend status.
        """
        if target_date is None:
            target_date = date.today()

        weekday = target_date.weekday()
        is_weekend = weekday in (5, 6)
        is_long_weekend, lw_desc = self.detect_long_weekend(target_date)
        direct_holiday = self.get_holiday_on_date(target_date)

        score = 15.0  # baseline weekday ambient
        active_holiday_name = None

        if direct_holiday:
            score = direct_holiday.impact_level
            active_holiday_name = direct_holiday.name
        elif is_long_weekend:
            score = 75.0
        elif is_weekend:
            score = 55.0
        else:
            # Check proximity to nearby holidays (within 3 days)
            for offset in [-3, -2, -1, 1, 2, 3]:
                near_date = target_date + timedelta(days=offset)
                near_h = self.get_holiday_on_date(near_date)
                if near_h:
                    # Dissipating proximity ripple
                    score = max(score, near_h.impact_level * (0.85 - abs(offset) * 0.15))
                    active_holiday_name = f"Near {near_h.name}"
                    break

        return {
            "score": round(min(100.0, max(0.0, score)), 1),
            "is_holiday": direct_holiday is not None,
            "holiday_name": active_holiday_name or ("Weekend" if is_weekend else None),
            "is_long_weekend": is_long_weekend,
            "weekend_status": lw_desc,
            "weekday": target_date.strftime("%A")
        }


holiday_engine = HolidayEngine()
