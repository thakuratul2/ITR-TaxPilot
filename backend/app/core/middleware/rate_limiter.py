"""Rate limiting middleware using Redis with in-memory fallback."""

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.cache.redis import get_redis_client
from app.core.config import get_settings
from app.schemas.base import APIError, APIResponse

logger = logging.getLogger("app.middleware.ratelimit")

# In-memory sliding window counters for fallback
_in_memory_ratelimit: dict[str, list[float]] = {}


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter per client IP backed by Redis with in-memory fallback."""

    EXEMPT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = getattr(getattr(request, "app", None), "state", None)
        settings = getattr(settings, "settings", None) or get_settings()

        # Check if rate limiting is enabled or path is exempt
        if not getattr(settings, "RATE_LIMIT_ENABLED", True) or request.url.path in self.EXEMPT_PATHS or request.url.path.startswith("/health"):
            return await call_next(request)

        # Extract client identifier
        client_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
            or (request.client.host if request.client else "unknown_client")
        )

        limit = getattr(settings, "RATE_LIMIT_PER_MINUTE", 60)
        window_seconds = 60
        now = time.time()
        current_minute = int(now // window_seconds)
        redis_key = f"taxpilot:ratelimit:{client_ip}:{current_minute}"
        reset_seconds = int(window_seconds - (now % window_seconds))

        current_count = 1
        redis_used = False

        try:
            client = await get_redis_client()
            if client is not None:
                try:
                    pipe = client.pipeline()
                    pipe.incr(redis_key)
                    pipe.expire(redis_key, window_seconds + 5)
                    results = await pipe.execute()
                    current_count = results[0]
                    redis_used = True
                except Exception as loop_err:
                    if "Event loop" in str(loop_err) or "closed" in str(loop_err):
                        from app.cache import redis as redis_mod
                        redis_mod._redis_client = None
                        client = await get_redis_client()
                        if client is not None:
                            pipe = client.pipeline()
                            pipe.incr(redis_key)
                            pipe.expire(redis_key, window_seconds + 5)
                            results = await pipe.execute()
                            current_count = results[0]
                            redis_used = True
                    else:
                        raise loop_err
        except Exception as exc:
            logger.debug("Redis rate limiting check failed, falling back to memory: %s", exc)

        if not redis_used:
            # In-memory fallback sliding window
            timestamps = _in_memory_ratelimit.get(client_ip, [])
            # Filter out entries older than 60 seconds
            valid_timestamps = [t for t in timestamps if now - t < window_seconds]
            valid_timestamps.append(now)
            _in_memory_ratelimit[client_ip] = valid_timestamps
            current_count = len(valid_timestamps)

        remaining = max(0, limit - current_count)

        # Enforce rate limit
        if current_count > limit:
            request_id = getattr(request.state, "request_id", "req_unknown")
            error_response = APIResponse(
                success=False,
                data=None,
                error=APIError(
                    code="RATE_LIMIT_EXCEEDED",
                    message="Too many requests. Please slow down and try again later.",
                    details={"limit_per_minute": limit, "retry_after_seconds": reset_seconds},
                ),
                request_id=request_id,
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=error_response.model_dump(),
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_seconds),
                    "Retry-After": str(reset_seconds),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_seconds)
        return response
