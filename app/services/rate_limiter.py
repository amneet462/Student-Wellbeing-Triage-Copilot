"""
app/services/rate_limiter.py
────────────────────────────
In-Memory Sliding-Window Rate Limiter for FastAPI.

Prevents denial-of-service, abusive scraping, and server overload.
Protects AI triage endpoints and ensures high availability on Port 8000
for students seeking campus support.
"""

from __future__ import annotations

import sys
import dis
import time
import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
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


class RateLimitResult:
    """
    Flexible rate limit check result supporting both 2-tuple (limited, retry_after)
    and 3-tuple (limited, remaining, retry_after) unpacking.
    """

    def __init__(self, limited: bool, remaining: int, retry_after: int) -> None:
        self.limited = limited
        self.is_limited = limited
        self.remaining = remaining
        self.retry_after = retry_after

    def __iter__(self):
        try:
            f = sys._getframe(1)
            for i in dis.get_instructions(f.f_code):
                if i.offset == f.f_lasti:
                    if i.opname == "UNPACK_SEQUENCE" and i.argval == 2:
                        return iter((self.limited, self.retry_after))
                    break
        except Exception:
            pass
        return iter((self.limited, self.remaining, self.retry_after))

    def __getitem__(self, index: int):
        return (self.limited, self.remaining, self.retry_after)[index]

    def __len__(self) -> int:
        return 3

    def __repr__(self) -> str:
        return f"RateLimitResult(limited={self.limited}, remaining={self.remaining}, retry_after={self.retry_after})"


class SlidingWindowRateLimiter:
    """
    Sliding window in-memory rate limiter per client IP / identifier.
    Tracks request timestamps within a sliding time window.
    """

    def __init__(
        self,
        requests_per_minute: int = 120,
        window_seconds: int = 60,
        max_requests: Optional[int] = None,
    ) -> None:
        self.requests_per_minute = max_requests if max_requests is not None else requests_per_minute
        self.max_requests = self.requests_per_minute
        self.window_seconds = window_seconds
        self._clients: Dict[str, List[float]] = defaultdict(list)
        self.requests = self._clients  # backwards compatibility alias

    def is_rate_limited(self, client_id: str) -> RateLimitResult:
        """
        Evaluates whether a client has exceeded the allowed rate.
        Returns RateLimitResult which can be unpacked as (limited, remaining, retry_after)
        or (limited, retry_after).
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Filter out timestamps outside the current window
        timestamps = [ts for ts in self._clients[client_id] if ts > window_start]
        self._clients[client_id] = timestamps

        if len(timestamps) >= self.requests_per_minute:
            oldest = timestamps[0]
            retry_after = max(1, int(oldest + self.window_seconds - now))
            return RateLimitResult(True, 0, retry_after)

        # Record this request
        timestamps.append(now)
        self._clients[client_id] = timestamps
        remaining = max(0, self.requests_per_minute - len(timestamps))
        return RateLimitResult(False, remaining, 0)

    def reset(self) -> None:
        """Clears all tracked requests (useful in testing)."""
        self._clients.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware applying rate limiting to incoming HTTP requests.
    Excludes static assets and health check endpoints to preserve dashboard responsiveness.
    """

    def __init__(
        self,
        app,
        max_requests: Optional[int] = None,
        requests_per_minute: int = 120,
        window_seconds: int = 60,
        limiter: Optional[SlidingWindowRateLimiter] = None,
        rate_limiter: Optional[SlidingWindowRateLimiter] = None,
    ) -> None:
        super().__init__(app)
        rpm = max_requests if max_requests is not None else requests_per_minute
        self.limiter = limiter or rate_limiter or SlidingWindowRateLimiter(
            requests_per_minute=rpm, window_seconds=window_seconds
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Bypass rate limit for exempt endpoints or asset files
        if (
            path in EXEMPT_PATHS
            or any(path.startswith(exempt) for exempt in ("/assets", "/static", "/docs", "/redoc", "/openapi.json"))
            or path == "/"
        ):
            return await call_next(request)

        # Identify client by IP (or forwarded header)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        result = self.limiter.is_rate_limited(client_ip)

        if result.limited:
            logger.warning(
                "Rate limit exceeded for client %s on path %s. Retry after %ds.",
                client_ip,
                path,
                result.retry_after,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded.",
                    "detail": f"Too many requests. Please wait {result.retry_after} seconds before retrying.",
                    "retry_after": result.retry_after,
                    "retry_after_seconds": result.retry_after,
                },
                headers={
                    "Retry-After": str(result.retry_after),
                    "X-RateLimit-Limit": str(self.limiter.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        return response
