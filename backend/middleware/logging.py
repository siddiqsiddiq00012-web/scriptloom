import logging
import time

from fastapi import Request

logger = logging.getLogger("scriptloom")


async def log_requests(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    duration = round((time.perf_counter() - start) * 1000, 2)

    logger.info(
        "%s %s %s %sms",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )

    return response