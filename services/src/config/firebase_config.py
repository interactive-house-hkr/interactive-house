import firebase_admin
from firebase_admin import credentials, db
from .settings import settings
from pathlib import Path

def init_firebase():
    if not firebase_admin._apps:
        # Resolve the service account path relative to the project root
        config_dir = Path(__file__).parent.parent.parent
        service_account_path = config_dir / settings.firebase_service_account

        cred = credentials.Certificate(str(service_account_path))
        firebase_admin.initialize_app(
            cred,
            {
                "projectId": settings.firebase_project_id,
                "databaseURL": settings.firebase_database_url,
            },
        )

def get_ref(path: str = "/"):
    init_firebase()
    return db.reference(path)
