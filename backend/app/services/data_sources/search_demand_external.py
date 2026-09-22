"""
External Search Demand Provider (Milestone 12 / Prompt 6).

Responsible for:
1. Providing an optional external search interest proxy (e.g. Google Trends / regional query volume)
   strictly segregated from first-party Yatri Setu user activity.
2. Caching responses with time-to-live (TTL) to prevent API rate-limiting (HTTP 429).
3. Rate-limiting requests to avoid external provider throttling.
4. Handling unavailable responses gracefully by returning DataSourceReading with UNAVAILABLE provenance.
5. Preserving strict provenance: NEVER overwriting or replacing first-party PostgreSQL demand telemetry.
6. Explicitly documenting that external search volume reflects online search curiosity, NOT physical tourist footfall.
"""

import time
import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timezone

from app.services.data_sources.base import (
    BaseDataSourceProvider,
    DataSourceReading,
    VALID_PROVIDER_MODES,
)

logger = logging.getLogger(__name__)

CANONICAL_DESTINATIONS = ("darjeeling", "kalimpong", "mirik", "lava", "lolegaon", "rishop")


class ExternalSearchDemandProvider(BaseDataSourceProvider):
    """
    External search demand aggregator for Eastern Himalayan hill circuits.
    Maintains rate limiting, in-memory TTL caching, and explicit provenance isolation.
    """

    PROVIDER_TYPE: str = "REAL"
    PROVIDER_MODE: str = "LIVE"

    def __init__(
        self,
        ttl_seconds: int = 3600,
        max_queries_per_minute: int = 15,
        enabled: bool = False
    ):
        self.ttl_seconds = ttl_seconds
        self.max_queries_per_minute = max_queries_per_minute
        self.enabled = enabled
        self._cache: Dict[str, Tuple[float, DataSourceReading]] = {}
        self._request_timestamps: list[float] = []

    def _check_rate_limit(self) -> bool:
        """Returns True if within rate limits, False otherwise."""
        now = time.time()
        # Keep timestamps from the last 60 seconds
        self._request_timestamps = [t for t in self._request_timestamps if now - t < 60.0]
        if len(self._request_timestamps) >= self.max_queries_per_minute:
            return False
        self._request_timestamps.append(now)
        return True

    def get_search_interest(
        self,
        destination_id: str,
        target_date: Optional[str] = None
    ) -> DataSourceReading:
        """
        Retrieves external search interest for a canonical destination.
        Returns DataSourceReading with explicit provenance and confidence.
        """
        dest_clean = destination_id.lower().strip()
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        if dest_clean not in CANONICAL_DESTINATIONS:
            return DataSourceReading(
                value=0.0,
                available=False,
                source="EXTERNAL_SEARCH_AGGREGATOR",
                confidence=0.0,
                unit="search_interest_index",
                timestamp=now_ts,
                notes=f"Destination '{dest_clean}' is not a recognized canonical circuit.",
                provider_mode="UNAVAILABLE",
                data_quality="LOW",
                signal_type="SEARCH_DEMAND"
            )

        cache_key = f"{dest_clean}:{target_date or 'latest'}"
        now_time = time.time()

        # Check cache
        if cache_key in self._cache:
            cache_time, cached_reading = self._cache[cache_key]
            if now_time - cache_time < self.ttl_seconds:
                # Return cached reading with CACHED mode
                return DataSourceReading(
                    value=cached_reading.value,
                    available=cached_reading.available,
                    source=cached_reading.source,
                    confidence=cached_reading.confidence,
                    raw_value=cached_reading.raw_value,
                    unit=cached_reading.unit,
                    timestamp=cached_reading.timestamp,
                    notes=f"Cached external search interest (TTL {self.ttl_seconds}s)",
                    provider_mode="CACHED",
                    data_quality=cached_reading.data_quality,
                    signal_type="SEARCH_DEMAND"
                )

        if not self.enabled:
            # External search provider intentionally disabled or unconfigured
            reading = DataSourceReading(
                value=0.0,
                available=False,
                source="EXTERNAL_SEARCH_AGGREGATOR",
                confidence=0.0,
                raw_value=None,
                unit="search_interest_index",
                timestamp=now_ts,
                notes=(
                    "External search provider (e.g. Google Trends) is unconfigured or disabled. "
                    "First-party PostgreSQL demand ledger remains authoritative."
                ),
                provider_mode="UNAVAILABLE",
                data_quality="LOW",
                signal_type="SEARCH_DEMAND"
            )
            return reading

        # Rate-limit enforcement
        if not self._check_rate_limit():
            logger.warning(f"External search demand rate limit reached ({self.max_queries_per_minute}/min).")
            return DataSourceReading(
                value=0.0,
                available=False,
                source="EXTERNAL_SEARCH_AGGREGATOR",
                confidence=0.0,
                unit="search_interest_index",
                timestamp=now_ts,
                notes="External search demand rate limit exceeded; falling back to UNAVAILABLE.",
                provider_mode="UNAVAILABLE",
                data_quality="DEGRADED",
                signal_type="SEARCH_DEMAND"
            )

        # In production, this can call an official search trend API if configured.
        # By default, external search returns UNAVAILABLE without fabricating values.
        reading = DataSourceReading(
            value=0.0,
            available=False,
            source="EXTERNAL_SEARCH_AGGREGATOR",
            confidence=0.0,
            raw_value=None,
            unit="search_interest_index",
            timestamp=now_ts,
            notes="No external search provider API connection configured.",
            provider_mode="UNAVAILABLE",
            data_quality="LOW",
            signal_type="SEARCH_DEMAND"
        )
        self._cache[cache_key] = (now_time, reading)
        return reading

    def get_reading(self, destination_id: str) -> DataSourceReading:
        """BaseDataSourceProvider conformance method."""
        return self.get_search_interest(destination_id)


# Singleton instance
external_search_provider = ExternalSearchDemandProvider()
