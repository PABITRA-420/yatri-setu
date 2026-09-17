"""
In-memory Rate Limiting and Abuse Protection for Yatri Setu (Milestone 7H).
Implements thread-safe sliding window rate limiting per client IP.
"""

import time
import threading
from typing import Dict, List, Optional
from fastapi import Request, HTTPException, status
from app.core.config import settings


class SlidingWindowRateLimiter:
    """
    Thread-safe sliding window rate limiter with auto-cleanup.
    Protects compute-heavy AI generation, public telemetry, SOS dispatch, and administrative refreshes.
    """

    def __init__(self, requests_per_minute: int = 60, burst_allowance: int = 10):
        self.limit = requests_per_minute + burst_allowance
        self.window_seconds = 60
        self._lock = threading.Lock()
        self._hits: Dict[str, List[float]] = {}
        self._last_cleanup = time.time()

    def _get_client_identifier(self, request: Request) -> str:
        """Extracts client IP or forward-header without leaking identity."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = getattr(request, "client", None)
        return client.host if client else "127.0.0.1"

    def check_rate_limit(self, request: Request):
        """
        FastAPI dependency callable.
        Raises HTTP 429 if the client exceeds the allowed window.
        """
        now = time.time()
        client_id = self._get_client_identifier(request)

        with self._lock:
            # Periodic cleanup of expired clients every 300 seconds
            if now - self._last_cleanup > 300:
                expired_threshold = now - self.window_seconds
                self._hits = {
                    cid: [t for t in timestamps if t > expired_threshold]
                    for cid, timestamps in self._hits.items()
                    if any(t > expired_threshold for t in timestamps)
                }
                self._last_cleanup = now

            client_history = self._hits.setdefault(client_id, [])
            cutoff = now - self.window_seconds

            # Filter timestamps within current window
            valid_hits = [t for t in client_history if t > cutoff]
            self._hits[client_id] = valid_hits

            if len(valid_hits) >= self.limit:
                oldest_in_window = valid_hits[0]
                retry_after = max(1, int(self.window_seconds - (now - oldest_in_window)))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Please retry after {retry_after} seconds.",
                    headers={"Retry-After": str(retry_after)}
                )

            # Record hit
            self._hits[client_id].append(now)


# Standard singleton limiters based on configuration
ai_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=settings.RATE_LIMIT_AI_PER_MINUTE)
sos_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=settings.RATE_LIMIT_SOS_PER_MINUTE)
general_rate_limiter = SlidingWindowRateLimiter(requests_per_minute=settings.RATE_LIMIT_GENERAL_PER_MINUTE)
