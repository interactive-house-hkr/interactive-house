import time
from fastapi import Request
from services.src.utils.logger import get_logger

logger = get_logger("middleware")

async def logging_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        f"{request.method} {request.url.path} "
        f"-> {response.status_code} "
        f"({duration_ms:.2f} ms)"
    )

    return response
