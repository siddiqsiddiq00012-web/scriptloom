import logging

from backend.core.config import settings
from backend.storage.local import LocalStorage
from backend.storage.r2 import R2Storage

logger = logging.getLogger("scriptloom.storage")

# R2 settings that must be present for the R2 backend to be usable.
# R2_ENDPOINT may be omitted when R2_ACCOUNT_ID is set (the standard
# Cloudflare R2 endpoint is derived from the account id). R2_PUBLIC_URL
# is optional and only used for direct public asset access.
R2_REQUIRED_ATTRS = (
    "R2_BUCKET_NAME",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
)


def _r2_endpoint_for(config) -> str:
    endpoint = (getattr(config, "R2_ENDPOINT", "") or "").strip()
    if not endpoint:
        account_id = (getattr(config, "R2_ACCOUNT_ID", "") or "").strip()
        if account_id:
            endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
    return endpoint


def build_storage(config=settings):
    """Instantiate the storage provider for the given configuration.

    Falls back to Local Storage (with an informative log) when the R2
    backend is requested but its credentials are incomplete, so startup
    never crashes on missing R2 configuration.
    """
    backend = (getattr(config, "STORAGE_BACKEND", "local") or "local").lower()

    if backend == "r2":
        missing = [name for name in R2_REQUIRED_ATTRS if not getattr(config, name, "")]
        endpoint = _r2_endpoint_for(config)

        if missing or not endpoint:
            logger.warning(
                "STORAGE_BACKEND is 'r2' but R2 configuration is incomplete "
                "(missing: %s; endpoint: %s). Falling back to Local Storage.",
                ", ".join(missing) if missing else "none",
                "set" if endpoint else "missing",
            )
            return LocalStorage(root_directory=config.LOCAL_STORAGE_ROOT)

        return R2Storage(
            endpoint_url=endpoint,
            bucket_name=config.R2_BUCKET_NAME,
            access_key_id=config.R2_ACCESS_KEY_ID,
            secret_access_key=config.R2_SECRET_ACCESS_KEY,
            account_id=getattr(config, "R2_ACCOUNT_ID", ""),
            public_url=getattr(config, "R2_PUBLIC_URL", ""),
        )

    return LocalStorage(root_directory=config.LOCAL_STORAGE_ROOT)


storage = build_storage()
