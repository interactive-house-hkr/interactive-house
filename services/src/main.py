from fastapi import FastAPI
import logging
import os

LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
def startup_event():
    logger.info("🚀 Server started")

@app.get("/")
def root():
    logger.info("GET / called")
    return {"status": "ok"}

