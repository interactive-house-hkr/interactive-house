from fastapi import FastAPI
from services.src.routes.device_routes import router as device_router
from services.src.routes.state_routes import router as state_router
from services.src.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Interactive House API", version="0.1.0")

@app.on_event("startup")
def startup_event():
    logger.info("🚀 Server started")

# Include routers
app.include_router(device_router, prefix="/api/v1")
app.include_router(state_router, prefix="/api/v1")

@app.get("/")
def root():
    logger.info("GET / called")
    return {"status": "ok"}
