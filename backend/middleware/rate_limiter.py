import ipaddress
import logging
import time
from typing import Tuple

from fastapi import Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.core.config import settings
from backend.core.token import extract_access_token

logger = logging.getLogger(__name__)


class RedisRateLimiter:
    def __init__(self, redis_url: str):
        import redis
        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._redis.ping()
        self._prefix = "rl:"

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        now = time.time()
        window_start = now - window_seconds
        redis_key = f"{self._prefix}{key}"

        pipe = self._redis.pipeline()
        pipe.zremrangebyscore(redis_key, 0, window_start)
        pipe.zcard(redis_key)
        pipe.zadd(redis_key, {str(now): now})
        pipe.expire(redis_key, window_seconds)
        results = pipe.execute()

        current_count = results[1]
        remaining = max(0, max_requests - current_count)

        if current_count >= max_requests:
            members = self._redis.zrange(redis_key, 0, 0)
            if members:
                oldest = float(members[0])
                retry_after = int(oldest + window_seconds - now) + 1
            else:
                retry_after = window_seconds
            return True, remaining, retry_after

        return False, remaining - 1, 0

    def close(self):
        try:
            self._redis.close()
        except Exception:
            pass


class MemoryRateLimiter:
    def __init__(self):
        self.requests: dict[str, list[float]] = {}

    def is_rate_limited(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        now = time.time()
        window_start = now - window_seconds

        if key not in self.requests:
            self.requests[key] = []

        self.requests[key] = [ts for ts in self.requests[key] if ts > window_start]

        current_count = len(self.requests[key])
        remaining = max(0, max_requests - current_count)

        if current_count >= max_requests:
            oldest = self.requests[key][0]
            retry_after = int(oldest + window_seconds - now) + 1
            return True, remaining, retry_after

        self.requests[key].append(now)
        return False, remaining - 1, 0

    def close(self):
        pass


def _get_rate_limiter():
    try:
        limiter = RedisRateLimiter(settings.REDIS_URL)
        logger.info("Rate limiter: using Redis backend")
        return limiter
    except Exception as e:
        logger.warning(f"Rate limiter: Redis unavailable ({e}), falling back to in-memory. "
                       "In-memory limiter is NOT suitable for production multi-worker deployments.")
        return MemoryRateLimiter()


rate_limiter_backend = _get_rate_limiter()


def _parse_trusted_proxies() -> list:
    raw = settings.RATE_LIMIT_TRUSTED_PROXIES
    result = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            result.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            result.append(ipaddress.ip_address(item))
    return result


def _extract_client_ip(request: Request) -> str:
    direct_ip = request.client.host if request.client else "127.0.0.1"

    if not _is_trusted_proxy(direct_ip):
        return direct_ip

    xff = request.headers.get("x-forwarded-for")
    if xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            return parts[0]

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    return direct_ip


_trusted_proxies = None

def _is_trusted_proxy(ip_str: str) -> bool:
    global _trusted_proxies
    if _trusted_proxies is None:
        _trusted_proxies = _parse_trusted_proxies()

    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False

    for network in _trusted_proxies:
        if isinstance(network, ipaddress.IPv4Network) or isinstance(network, ipaddress.IPv6Network):
            if ip in network:
                return True
        elif ip == network:
            return True
    return False


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        client_ip = _extract_client_ip(request)

        if "/auth/login" in path or "/auth/register" in path:
            max_reqs = settings.RATE_LIMIT_AUTH
            tier_name = "auth"
        elif "/media" in path and request.method == "POST":
            max_reqs = settings.RATE_LIMIT_UPLOAD
            tier_name = "upload"
        elif "/generation" in path and request.method == "POST":
            max_reqs = settings.RATE_LIMIT_AI
            tier_name = "ai"
        elif extract_access_token(request) is not None:
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
