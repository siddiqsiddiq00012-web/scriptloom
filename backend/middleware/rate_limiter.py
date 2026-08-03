import time
from abc import ABC, abstractmethod
from typing import Dict, Tuple
from fastapi import HTTPException, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from backend.core.config import settings


class BaseRateLimiterBackend(ABC):
    @abstractmethod
    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        pass


class MemoryRateLimiter(BaseRateLimiterBackend):
    def __init__(self):
        # key -> list of timestamps
        self.requests: Dict[str, list] = {}

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        now = time.time()
        window_start = now - window_seconds

        if key not in self.requests:
            self.requests[key] = []

        # Filter out expired timestamps
        self.requests[key] = [ts for ts in self.requests[key] if ts > window_start]

        current_count = len(self.requests[key])
        remaining = max(0, max_requests - current_count)

        if current_count >= max_requests:
            oldest = self.requests[key][0]
            retry_after = int(oldest + window_seconds - now) + 1
            return True, remaining, retry_after

        self.requests[key].append(now)
        return False, remaining - 1, 0


# Global Rate Limiter Backend Instance
rate_limiter_backend = MemoryRateLimiter()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        client_ip = request.client.host if request.client else "127.0.0.1"

        # Determine threshold based on endpoint tier
        if "/auth/login" in path or "/auth/register" in path:
            max_reqs = settings.RATE_LIMIT_AUTH
            tier_name = "auth"
        elif "/media" in path and request.method == "POST":
            max_reqs = settings.RATE_LIMIT_UPLOAD
            tier_name = "upload"
        elif "/generation" in path and request.method == "POST":
            max_reqs = settings.RATE_LIMIT_AI
            tier_name = "ai"
        elif "Authorization" in request.headers:
            max_reqs = settings.RATE_LIMIT_AUTHENTICATED
            tier_name = "authenticated"
        else:
            max_reqs = settings.RATE_LIMIT_ANONYMOUS
            tier_name = "anonymous"

        rate_key = f"{client_ip}:{tier_name}"
        is_limited, remaining, retry_after = rate_limiter_backend.is_rate_limited(
            key=rate_key,
            max_requests=max_reqs,
            window_seconds=60,
        )

        if is_limited:
            return Response(
                content=f'{{"detail": "Too Many Requests. Rate limit exceeded for {tier_name} endpoint."}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_reqs),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_reqs)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
