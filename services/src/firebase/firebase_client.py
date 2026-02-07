import firebase_admin
from firebase_admin import credentials, db
from services.src.config.settings import settings
from pathlib import Path
from services.src.utils.logger import get_logger

logger = get_logger(__name__)

def init_firebase():
    if not firebase_admin._apps:
        # Project root (interactive-house/)
        project_root = Path(__file__).resolve().parents[3]
        # The key file should be located in services/src/config/
        service_account_path = project_root / "services" / "src" / "config" / settings.firebase_service_account

        logger.info("Initializing Firebase")
        logger.debug(f"Using service account: {service_account_path}")

        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(
            cred,
            {
                "projectId": settings.firebase_project_id,
                "databaseURL": settings.firebase_database_url,
            },
        )
        logger.info("Firebase initialized")

def get_ref(path: str = "/"):
    init_firebase()
    logger.debug(f"Getting Firebase DB reference for path: {path}")
    return db.reference(path)
