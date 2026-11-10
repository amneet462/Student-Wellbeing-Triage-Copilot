"""
app/services/rate_limiter.py
────────────────────────────
In-Memory Sliding-Window Rate Limiter for FastAPI.

Prevents denial-of-service, abusive scraping, and server overload.
Protects AI triage endpoints and ensures high availability on Port 8000.
"""

from __future__ import annotations

import time
import logging
from collections import defaultdict
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter tracking request timestamps per client identifier (IP).
    """

    def __init__(self, requests_per_minute: int = 120, window_seconds: int = 60) -> None:
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self._clients: Dict[str, List[float]] = defaultdict(list)

    def is_rate_limited(self, client_id: str) -> Tuple[bool, int, int]:
        """
        Evaluates whether a client has exceeded the allowed rate.
        Returns:
            (is_limited: bool, remaining_requests: int, retry_after_seconds: int)
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Filter out timestamps outside the current window
        timestamps = [ts for ts in self._clients[client_id] if ts > window_start]
        self._clients[client_id] = timestamps

        if len(timestamps) >= self.requests_per_minute:
            oldest = timestamps[0]
            retry_after = max(1, int(oldest + self.window_seconds - now))
            return True, 0, retry_after

        # Record this request
        timestamps.append(now)
        self._clients[client_id] = timestamps
        remaining = max(0, self.requests_per_minute - len(timestamps))
        return False, remaining, 0

    def reset(self) -> None:
        """Clears all tracked clients (used in tests)."""
        self._clients.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware applying rate limiting to incoming HTTP requests.
    Excludes static assets and health check endpoints to preserve dashboard responsiveness.
    """

    EXEMPT_PATHS = (
        "/api/triage/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/assets",
        "/static",
    )

    def __init__(self, app, rate_limiter: SlidingWindowRateLimiter | None = None) -> None:
        super().__init__(app)
        self.limiter = rate_limiter or SlidingWindowRateLimiter(requests_per_minute=120, window_seconds=60)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Exempt paths from rate limiting
        if any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS) or path == "/":
            return await call_next(request)

        # Identify client by IP (or forwarded header)
        client_ip = request.client.host if request.client else "127.0.0.1"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()

        is_limited, remaining, retry_after = self.limiter.is_rate_limited(client_ip)

        if is_limited:
            logger.warning("Rate limit exceeded for client %s on path %s", client_ip, path)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded.",
                    "detail": f"Too many requests. Please wait {retry_after} seconds before retrying.",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.limiter.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
