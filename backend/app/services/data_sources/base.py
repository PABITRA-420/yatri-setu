"""
Base interface for all Yatri Setu data source providers.

Each data source must implement a MOCK provider for MVP.
The architecture allows swapping in REAL providers later
without changing the Crowd Engine V2.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


VALID_PROVIDER_MODES = (
    "REAL", "LIVE", "CACHED", "HISTORICAL", "COMPUTED",
    "SYNTHETIC", "DEMO", "MOCK", "UNAVAILABLE"
)

@dataclass
class DataSourceReading:
    """
    Normalized reading from any data source.
    Value is always 0.0–100.0 (fully normalized).
    """
    value: float                   # 0-100, normalized pressure indicator
    available: bool = True
    source: str = "MOCK"
    confidence: float = 1.0        # 0.0–1.0 confidence in this reading
    raw_value: Optional[float] = None   # original un-normalized value
    unit: str = ""                  # e.g. "percent", "count", "index"
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    notes: str = ""
    provider_mode: str = "MOCK"    # LIVE, CACHED, HISTORICAL, COMPUTED, SYNTHETIC, DEMO, MOCK, UNAVAILABLE
    data_quality: str = "HIGH"     # HIGH, MEDIUM, LOW, DEGRADED
    signal_type: str = "UNKNOWN"

    def __post_init__(self):
        self.value = max(0.0, min(100.0, self.value))
        self.confidence = max(0.0, min(1.0, self.confidence))
        if self.provider_mode.upper() in VALID_PROVIDER_MODES:
            self.provider_mode = self.provider_mode.upper()
        else:
            self.provider_mode = "MOCK"
        if self.data_quality not in ("HIGH", "MEDIUM", "LOW", "DEGRADED"):
            self.data_quality = "HIGH"


class BaseDataSourceProvider(ABC):
    """
    Abstract interface every data source must implement.
    
    Implementations:
      - MOCK provider: deterministic, seeded, always available
      - REAL provider: external API / database, may fail gracefully
      - CACHED provider: serving recent cached data
    """
    PROVIDER_TYPE: str = "MOCK"   # "MOCK", "REAL", or "CACHED"
    PROVIDER_MODE: str = "MOCK"

    @abstractmethod
    def get_reading(self, destination_id: str, date_str: Optional[str] = None) -> DataSourceReading:
        """Return a normalized pressure reading for a destination."""
        ...

    def is_available(self) -> bool:
        """Whether this provider is currently reachable."""
        return True

    def get_mode(self) -> str:
        """Return provider mode: MOCK, REAL, or CACHED."""
        return self.PROVIDER_MODE

    def get_unavailable_reading(self, reason: str = "Provider unavailable") -> DataSourceReading:
        """Return a safe fallback reading when provider is unavailable."""
        return DataSourceReading(
            value=50.0,   # neutral fallback
            available=False,
            source=self.PROVIDER_TYPE,
            confidence=0.0,
            notes=reason,
            provider_mode="UNAVAILABLE",
            data_quality="DEGRADED"
        )

