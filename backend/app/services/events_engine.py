"""
Events Engine for Yatri Setu.
Tracks regional Himalayan festivals, cultural events, sports meets,
and tourism carnivals, calculating event pressure on local infrastructure.
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Dict


@dataclass
class RegionalEvent:
    id: str
    name: str
    destination_ids: List[str]  # destinations directly affected
    start_month: int
    start_day: int
    end_month: int
    end_day: int
    category: str  # cultural, festival, sports, agricultural
    expected_daily_crowd: int
    pressure_intensity: float  # 0.0 to 100.0
    description: str


# Realistic Himalayan & West Bengal events catalog
SEED_EVENTS: List[RegionalEvent] = [
    RegionalEvent(
        id="darj-carnival",
        name="Darjeeling Winter Carnival",
        destination_ids=["darjeeling"],
        start_month=11,
        start_day=20,
        end_month=12,
        end_day=5,
        category="cultural",
        expected_daily_crowd=8000,
        pressure_intensity=85.0,
        description="Famous annual winter festival celebrating Darjeeling music, tea, food, and culture."
    ),
    RegionalEvent(
        id="losar-fest",
        name="Losar (Tibetan New Year)",
        destination_ids=["darjeeling", "kalimpong", "lava"],
        start_month=2,
        start_day=10,
        end_month=2,
        end_day=25,
        category="festival",
        expected_daily_crowd=5000,
        pressure_intensity=75.0,
        description="Traditional Tibetan Buddhist celebration with monastery cham dances and prayers."
    ),
    RegionalEvent(
        id="kalimpong-flower",
        name="Kalimpong Orchid & Flower Show",
        destination_ids=["kalimpong"],
        start_month=4,
        start_day=1,
        end_month=4,
        end_day=15,
        category="agricultural",
        expected_daily_crowd=4000,
        pressure_intensity=65.0,
        description="Celebrated horticultural festival highlighting exotic orchids and Himalayan blooms."
    ),
    RegionalEvent(
        id="teesta-adventure",
        name="Teesta White Water Rafting Fest",
        destination_ids=["kalimpong", "darjeeling"],
        start_month=10,
        start_day=15,
        end_month=11,
        end_day=10,
        category="sports",
        expected_daily_crowd=3500,
        pressure_intensity=60.0,
        description="Annual autumn river rafting and eco-adventure gathering along the Teesta."
    ),
    RegionalEvent(
        id="mirik-cherry",
        name="Mirik Lake Cherry Blossom Showcase",
        destination_ids=["mirik"],
        start_month=11,
        start_day=5,
        end_month=11,
        end_day=25,
        category="cultural",
        expected_daily_crowd=3000,
        pressure_intensity=55.0,
        description="Blooming of wild Himalayan cherry trees around Sumendu Lake."
    ),
    RegionalEvent(
        id="lava-nature-trail",
        name="Neora Valley Canopy & Birding Meet",
        destination_ids=["lava", "rishop"],
        start_month=3,
        start_day=10,
        end_month=3,
        end_day=25,
        category="agricultural",
        expected_daily_crowd=800,
        pressure_intensity=35.0,
        description="Eco-tourism and ornithology gathering in Neora Valley National Park borders."
    ),
    RegionalEvent(
        id="buddha-jayanti",
        name="Buddha Purnima Monastic Procession",
        destination_ids=["darjeeling", "kalimpong", "lolegaon"],
        start_month=5,
        start_day=15,
        end_month=5,
        end_day=23,
        category="festival",
        expected_daily_crowd=4500,
        pressure_intensity=70.0,
        description="Mass peace rallies and prayer ceremonies across Ghoom and Zang Dhok Palri monasteries."
    ),
    RegionalEvent(
        id="autumn-tea-harvest",
        name="Autumn Flush Tea Festival",
        destination_ids=["darjeeling", "mirik"],
        start_month=10,
        start_day=1,
        end_month=10,
        end_day=15,
        category="cultural",
        expected_daily_crowd=6000,
        pressure_intensity=75.0,
        description="Harvest festival showcasing world-renowned autumn flush black teas."
    )
]


class EventsEngine:
    """Manages active events and calculates crowd/infrastructure pressure."""

    def __init__(self, events: Optional[List[RegionalEvent]] = None):
        self.events = events or SEED_EVENTS

    def _is_date_in_event(self, target_date: date, event: RegionalEvent) -> bool:
        """Check if target date falls within event's recurring annual window."""
        t_month = target_date.month
        t_day = target_date.day

        # Same month range
        if event.start_month == event.end_month:
            return (t_month == event.start_month and
                    event.start_day <= t_day <= event.end_day)

        # Crosses month boundary (same year)
        if event.start_month < event.end_month:
            if t_month == event.start_month and t_day >= event.start_day:
                return True
            if t_month == event.end_month and t_day <= event.end_day:
                return True
            if event.start_month < t_month < event.end_month:
                return True
            return False

        # Crosses year end (e.g., Dec to Jan)
        if event.start_month > event.end_month:
            if t_month == event.start_month and t_day >= event.start_day:
                return True
            if t_month == event.end_month and t_day <= event.end_day:
                return True
            if t_month > event.start_month or t_month < event.end_month:
                return True
            return False

        return False

    def get_active_events_for_destination(
        self, destination_id: str, target_date: Optional[date] = None
    ) -> List[RegionalEvent]:
        """Find all active events affecting destination on date."""
        if target_date is None:
            target_date = date.today()

        matched = []
        dest_clean = destination_id.lower().strip()
        for ev in self.events:
            if dest_clean in [d.lower() for d in ev.destination_ids]:
                if self._is_date_in_event(target_date, ev):
                    matched.append(ev)
        return matched

    def calculate_event_pressure(
        self, destination_id: str, target_date: Optional[date] = None
    ) -> Dict:
        """
        Calculate composite event pressure (0-100) and details.
        Returns:
            {
                "score": float,
                "active_events": List[Dict],
                "summary": str
            }
        """
        active = self.get_active_events_for_destination(destination_id, target_date)
        if not active:
            return {
                "score": 10.0,  # baseline ambient event pressure
                "active_events": [],
                "summary": "No major scheduled festivals or sporting events active."
            }

        # Highest intensity event provides foundation, secondary events add additive pressure
        sorted_events = sorted(active, key=lambda x: x.pressure_intensity, reverse=True)
        primary = sorted_events[0].pressure_intensity
        additive = sum(e.pressure_intensity * 0.15 for e in sorted_events[1:])
        score = min(100.0, primary + additive)

        active_summaries = [
            {
                "id": e.id,
                "name": e.name,
                "category": e.category,
                "intensity": e.pressure_intensity,
                "expected_crowd": e.expected_daily_crowd,
                "description": e.description
            }
            for e in active
        ]

        summary = f"{len(active)} event(s) active: " + ", ".join(e.name for e in active)
        return {
            "score": round(score, 1),
            "active_events": active_summaries,
            "summary": summary
        }


events_engine = EventsEngine()
