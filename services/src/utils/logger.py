import logging
from services.src.config.settings import settings

LOG_LEVEL = settings.log_level.upper()
LOG_LEVEL_NUM = getattr(logging, LOG_LEVEL, logging.INFO)

logging.basicConfig(
    level=LOG_LEVEL_NUM,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

def get_logger(name: str):
    return logging.getLogger(name)
