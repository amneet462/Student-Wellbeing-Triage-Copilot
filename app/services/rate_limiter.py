"""
app/services/rate_limiter.py
────────────────────────────
<<<<<<< HEAD
In-Memory Sliding-Window Rate Limiter for FastAPI.

Prevents denial-of-service, abusive scraping, and server overload.
Protects AI triage endpoints and ensures high availability on Port 8000.
=======
In-memory sliding window rate limiter middleware for FastAPI.
Protects university endpoints from abuse and denial-of-service,
ensuring high availability for students in distress.
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
"""

from __future__ import annotations

<<<<<<< HEAD
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
=======
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
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
        """
        now = time.time()
        window_start = now - self.window_seconds

<<<<<<< HEAD
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
=======
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
>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
<<<<<<< HEAD
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
=======
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

>>>>>>> 7b1312e521408877fa3e722aab648c5edeaa4dad
