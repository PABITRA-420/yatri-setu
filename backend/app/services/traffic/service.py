"""
Traffic Service for Yatri Setu (Milestone 7C).
Manages corridor telemetry caching, access status determination, and deterministic traffic impact calculations.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

from app.core.config import settings
from app.services.traffic.base import BaseTrafficProvider
from app.services.traffic.provider import (
    TomTomTrafficProvider,
    DemoTrafficProvider,
    RealTrafficProvider,
    UnavailableTrafficProvider
)
from app.services.traffic.schemas import DestinationTrafficSummary, TrafficImpactSignal

logger = logging.getLogger(__name__)

DEFAULT_TRAFFIC_TTL_SECONDS = 300  # 5 minutes


class TrafficService:
    """
    Provider-agnostic traffic coordinator with corridor-level aggregation,
    TTL caching, stale fallback, and deterministic impact modeling.
    """

    def __init__(self, ttl_seconds: int = DEFAULT_TRAFFIC_TTL_SECONDS, provider: Optional[BaseTrafficProvider] = None):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._provider: BaseTrafficProvider = provider if provider is not None else self._initialize_provider()

    def _initialize_provider(self) -> BaseTrafficProvider:
        mode = (settings.TRAFFIC_PROVIDER or "demo").lower().strip()
        if mode in ("real", "tomtom", "google"):
            return TomTomTrafficProvider()
        elif mode == "unavailable":
            return UnavailableTrafficProvider()
        return DemoTrafficProvider()

    def set_provider(self, provider: BaseTrafficProvider):
        """Allows runtime or test provider swapping."""
        self._provider = provider

    def get_traffic(self, destination_id: str, force_refresh: bool = False) -> DestinationTrafficSummary:
        """
        Retrieves arterial traffic summary for a destination with caching.
        Employs graceful fallback: if provider fails, returns stale real cache or labeled safe fallback.
        Never caches demo fallback.
        """
        dest_clean = destination_id.lower().strip()
        now = datetime.utcnow()
        cached_entry = self._cache.get(dest_clean)

        # Check valid unexpired cache (Requirement 6 & 11)
        if not force_refresh and cached_entry:
            expires_at = cached_entry["expires_at"]
            if now < expires_at:
                summary: DestinationTrafficSummary = cached_entry["summary"].model_copy()
                summary.cache_status = "CACHED"
                summary.expires_at = expires_at
                # Retain REAL provenance from the cached real observation
                return summary

        # If configured provider is explicitly Demo or Unavailable, fetch directly without real caching
        if not isinstance(self._provider, TomTomTrafficProvider):
            return self._provider.fetch_traffic(dest_clean)

        # Provider is TomTom: attempt live fetch
        try:
            fresh_summary = self._provider.fetch_traffic(dest_clean)
            expires_at = now + timedelta(seconds=self.ttl_seconds)
            fresh_summary.expires_at = expires_at
            fresh_summary.cache_status = "LIVE"

            # Requirement 6: Cache only successful real observations with a short TTL
            self._cache[dest_clean] = {
                "summary": fresh_summary,
                "expires_at": expires_at,
                "cached_at": now
            }
            return fresh_summary

        except Exception as ex:
            logger.warning(f"Traffic provider error for {dest_clean}: {ex}. Checking safe fallback.")
            
            # If we had a previously cached genuine REAL observation, return stale REAL cache
            if cached_entry:
                stale_summary: DestinationTrafficSummary = cached_entry["summary"].model_copy()
                stale_summary.cache_status = "STALE"
                stale_summary.data_quality = "DEGRADED"
                stale_summary.confidence = max(0.4, stale_summary.confidence * 0.7)
                # Requirement 7 & 9: Real provenance retained as stale
                stale_summary.provenance_label = "REAL — TOMTOM TRAFFIC (STALE CACHE)"
                return stale_summary

            # Requirement 7 & 8: If TomTom genuinely fails and no cache exists, return an explicitly labeled safe fallback:
            # DEMO MODE — SYNTHETIC DATA or UNAVAILABLE — SAFE FALLBACK.
            # Do NOT cache this in self._cache!
            fallback = DemoTrafficProvider().fetch_traffic(dest_clean)
            fallback.cache_status = "STALE"
            fallback.data_quality = "DEGRADED"
            fallback.confidence = 0.50
            fallback.provider_mode = "DEMO"
            fallback.source = "DEMO_HIMALAYAN_CORRIDOR_TELEMETRY"
            fallback.provenance_label = "DEMO MODE — SYNTHETIC DATA"
            return fallback

    def calculate_traffic_impact(self, summary: DestinationTrafficSummary) -> TrafficImpactSignal:
        """
        Deterministic, transparent traffic impact calculation for destination pressure.
        Evaluates travel-time ratio, congestion level, and road accessibility.
        """
        ratio = summary.average_travel_time_ratio
        anomaly = summary.travel_time_anomaly_percent
        access = summary.access_status
        bottleneck = summary.primary_bottleneck_route
        incidents = summary.incident_count

        # Map to traffic status
        if ratio >= 1.8:
            status = "CRITICAL"
        elif ratio >= 1.4:
            status = "HIGH"
        elif ratio >= 1.15:
            status = "ELEVATED"
        else:
            status = "NORMAL"

        # Impact description
        if access == "DISRUPTED":
            desc = "Critical arterial road disruption: one or more access routes are closed. Travel severely impacted."
        elif status == "CRITICAL":
            desc = f"Severe corridor congestion (+{anomaly:.0f}% vs historical norm). Bottleneck: {bottleneck or 'Arterial road'}."
        elif status == "HIGH":
            desc = f"Heavy mountain traffic (+{anomaly:.0f}% travel time). Expect substantial delay on {bottleneck or 'access corridor'}."
        elif status == "ELEVATED":
            desc = f"Elevated traffic on access corridor (+{anomaly:.0f}% travel time). Moderate delays at regional checkpoints."
        else:
            desc = "Normal mountain corridor transit. Arterial access routes are clear and operating near historical baselines."

        return TrafficImpactSignal(
            destination_id=summary.destination_id,
            traffic_impact_score=summary.overall_congestion_score,
            traffic_status=status,
            travel_time_anomaly_percent=anomaly,
            access_status=access,
            bottleneck_corridor=bottleneck,
            impact_description=desc,
            confidence=summary.confidence,
            source=summary.source,
            provider_mode=summary.provider_mode,
            observed_at=summary.observed_at
        )

    def get_traffic_impact(self, destination_id: str) -> TrafficImpactSignal:
        """Helper to get current traffic and compute its impact signal in one step."""
        summary = self.get_traffic(destination_id)
        return self.calculate_traffic_impact(summary)


# Global Singleton Instance
traffic_service = TrafficService()
