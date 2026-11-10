"""
app/services/rate_limiter.py
────────────────────────────
In-memory sliding window rate limiter middleware for FastAPI.
Protects university endpoints from abuse and denial-of-service,
ensuring high availability for students in distress.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Dict, List, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

EXEMPT_PATHS = {
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/triage/health",
    "/api/triage/categories",
    "/favicon.ico",
}


class SlidingWindowRateLimiter:
    """
    Sliding window in-memory rate limiter per client IP.
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_rate_limited(self, client_ip: str) -> tuple[bool, int]:
        """
        Returns (is_limited, retry_after_seconds).
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Prune timestamps outside current window
        valid_timestamps = [t for t in self.requests[client_ip] if t > window_start]
        self.requests[client_ip] = valid_timestamps

        if len(valid_timestamps) >= self.max_requests:
            oldest = valid_timestamps[0]
            retry_after = max(1, int(oldest + self.window_seconds - now))
            return True, retry_after

        self.requests[client_ip].append(now)
        return False, 0

    def reset(self) -> None:
        """Clears all tracked requests (useful in testing)."""
        self.requests.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware enforcing sliding window rate limits.
    """

    def __init__(
        self,
        app,
        max_requests: int = 60,
        window_seconds: int = 60,
        limiter: Optional[SlidingWindowRateLimiter] = None,
    ) -> None:
        super().__init__(app)
        self.limiter = limiter or SlidingWindowRateLimiter(
            max_requests=max_requests, window_seconds=window_seconds
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Bypass rate limit for exempt endpoints or asset files
        if path in EXEMPT_PATHS or path.startswith("/assets") or path.startswith("/static"):
            return await call_next(request)

        # Extract client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        is_limited, retry_after = self.limiter.is_rate_limited(client_ip)
        if is_limited:
            logger.warning(
                "Rate limit exceeded for IP %s on %s. Retry after %ds.",
                client_ip,
                path,
                retry_after,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": "Too many requests. Please slow down and try again.",
                    "retry_after_seconds": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        response = await call_next(request)
        return response

