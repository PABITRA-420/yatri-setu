"""
Base Ingestor Contract (Milestone 6B).

Every data ingestor MUST:
  1. Return IngestedObservation records.
  2. Declare provider_mode: REAL | MOCK | CACHED | ESTIMATED | MISSING.
  3. Attach source, timestamp, confidence, and data_quality to every record.
  4. Never fabricate REAL provider modes unless actually connected to live data.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ProviderMode(str, Enum):
    """Strict data provenance labels used on every observation."""
    REAL = "REAL"
    MOCK = "MOCK"
    CACHED = "CACHED"
    ESTIMATED = "ESTIMATED"
    MISSING = "MISSING"


class IngestedObservation(BaseModel):
    """
    Normalized single-signal observation record with full data provenance.

    This is the fundamental unit of data flowing through the ingestion pipeline.
    Each field is mandatory; 'MISSING' provider_mode is used to explicitly
    represent unavailable data rather than silently omitting records.
    """
    destination_id: str = Field(description="Target destination identifier (lowercase)")
    date: str = Field(description="Observation date in YYYY-MM-DD format")
    signal_name: str = Field(description="e.g. 'weather_pressure', 'booking_demand'")
    signal_value: float = Field(ge=0.0, le=100.0, description="Normalized 0–100 pressure-equivalent score")

    # Raw metadata (optional, signal-type specific)
    raw_value: Optional[float] = Field(default=None, description="Original un-normalized value before scaling")
    raw_unit: Optional[str] = Field(default=None, description="Unit of the raw value (e.g. °C, mm, %)")

    # Data provenance — mandatory fields
    source: str = Field(description="Human-readable data source label, e.g. 'Yatri Setu Network', 'OpenWeatherMap'")
    provider_mode: ProviderMode = Field(description="REAL | MOCK | CACHED | ESTIMATED | MISSING")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the observation accuracy (0–1)")
    data_quality: str = Field(
        default="HIGH",
        description="Quality tier: HIGH | MEDIUM | LOW | DEGRADED"
    )

    # Optional extended context
    notes: Optional[str] = Field(default=None, description="Ingestor-specific annotation or caveats")


class BaseIngestor(ABC):
    """
    Abstract contract for all Yatri Setu data ingestors.

    Subclasses declare their provider_mode and source_label, then
    implement _fetch_real() and _fetch_mock() separately to ensure
    REAL vs MOCK paths are never accidentally mixed.
    """

    @property
    @abstractmethod
    def source_label(self) -> str:
        """Human-readable name of the data provider."""

    @property
    @abstractmethod
    def signal_name(self) -> str:
        """The signal this ingestor produces (e.g. 'weather_pressure')."""

    @property
    @abstractmethod
    def provider_mode(self) -> ProviderMode:
        """Current operating mode; determines which fetch path is used."""

    def ingest(self, destination_id: str, date: str) -> IngestedObservation:
        """
        Public entry point: fetch data and return a normalized observation.
        Routes to REAL or MOCK provider based on provider_mode.
        """
        try:
            if self.provider_mode == ProviderMode.REAL:
                return self._fetch_real(destination_id, date)
            else:
                return self._fetch_mock(destination_id, date)
        except Exception as exc:
            return self._missing(destination_id, date, reason=str(exc))

    @abstractmethod
    def _fetch_real(self, destination_id: str, date: str) -> IngestedObservation:
        """
        Fetch from a live external or first-party source.
        MUST only be called when provider_mode == REAL.
        MUST raise an exception if the real source is unavailable.
        """

    @abstractmethod
    def _fetch_mock(self, destination_id: str, date: str) -> IngestedObservation:
        """
        Deterministic simulation with no external dependency.
        MUST label provider_mode as MOCK and source as 'Mock Simulator'.
        """

    def _missing(self, destination_id: str, date: str, reason: str = "") -> IngestedObservation:
        """Produce an explicit MISSING record when fetch fails."""
        return IngestedObservation(
            destination_id=destination_id,
            date=date,
            signal_name=self.signal_name,
            signal_value=50.0,  # neutral fallback
            source="Signal Unavailable",
            provider_mode=ProviderMode.MISSING,
            confidence=0.0,
            data_quality="DEGRADED",
            notes=f"Signal unavailable: {reason}" if reason else "Signal unavailable",
        )
