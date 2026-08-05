from backend.core.config import settings
from backend.storage.local import LocalStorage
from backend.storage.r2 import R2Storage

if settings.STORAGE_BACKEND.lower() == "r2":
    storage = R2Storage(
        endpoint_url=settings.R2_ENDPOINT_URL,
        bucket_name=settings.R2_BUCKET_NAME,
        access_key_id=settings.R2_ACCESS_KEY_ID,
        secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    )
else:
    storage = LocalStorage(
        root_directory=settings.LOCAL_STORAGE_ROOT,
    )