import asyncio
from fastapi import FastAPI
from services.src.middleware.logging_middleware import logging_middleware
from services.src.routes.device_routes import router as device_router
from services.src.routes.state_routes import router as state_router
from services.src.utils.logger import get_logger
from services.src.bridge.bridge import run_bridge
from services.src.config.bridge_config import ENABLE_BRIDGE
from fastapi.middleware.cors import CORSMiddleware

logger = get_logger(__name__)

app = FastAPI(title="Interactive House API", version="0.1.0")

app.middleware("http")(logging_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify allowed origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task reference
bridge_task = None

@app.on_event("startup")
async def startup_event():
    global bridge_task
    logger.info("Server started")
    
    # Start bridge as background task if enabled
    if ENABLE_BRIDGE:
        logger.info("Starting bridge service...")
        bridge_task = asyncio.create_task(run_bridge())
    else:
        logger.info("Bridge service disabled")

@app.on_event("shutdown")
async def shutdown_event():
    global bridge_task
    logger.info("Server shutting down")
    
    if bridge_task and not bridge_task.done():
        logger.info("Stopping bridge service...")
        bridge_task.cancel()
        try:
            await bridge_task
        except asyncio.CancelledError:
            logger.info("Bridge service stopped")

# Include routers
app.include_router(device_router, prefix="/api/v1")
app.include_router(state_router, prefix="/api/v1")

@app.get("/")
def root():
    logger.info("GET / called")
    return {"status": "ok"}
