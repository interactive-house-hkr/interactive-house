from fastapi import FastAPI
import logging

# Basic logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
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
