import time
from fastapi import Request
from services.src.utils.logger import get_logger

logger = get_logger("middleware")
QUIET_PATH_SUFFIXES = {
    "/commands/next",
    "/heartbeat",
}

async def logging_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000
    path = request.url.path

    if any(path.endswith(suffix) for suffix in QUIET_PATH_SUFFIXES):
        logger.debug(
            f"{request.method} {request.url} "
            f"-> {response.status_code} "
            f"({duration_ms:.2f} ms)"
        )
        return response

    logger.info(
        f"{request.method} {request.url} "
        f"-> {response.status_code} "
        f"({duration_ms:.2f} ms)"
    )

    return response
