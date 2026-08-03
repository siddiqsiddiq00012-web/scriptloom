import logging
from typing import Optional
from sqlalchemy.orm import Session
from backend.models.audit_log import AuditLog
from backend.middleware.request_id import get_current_request_id

logger = logging.getLogger("scriptloom.audit")


class AuditLogger:
    @staticmethod
    def log_event(
        db: Optional[Session],
        action: str,
        resource: str = "",
        user_id: Optional[int] = None,
        ip_address: str = "",
        status: str = "SUCCESS",
        metadata: Optional[dict] = None,
    ):
        req_id = get_current_request_id()

        # Application Security Log
        logger.info(
            f"[AUDIT] req_id={req_id} user_id={user_id} ip={ip_address} action={action} resource={resource} status={status}"
        )

        # DB Immutable Record Storage if DB session is active
        if db:
            try:
                entry = AuditLog(
                    request_id=req_id,
                    user_id=user_id,
                    ip_address=ip_address,
                    action=action,
                    resource=resource,
                    status=status,
                    metadata_json=metadata or {},
                )
                db.add(entry)
                db.commit()
            except Exception as exc:
                logger.error(f"Failed to record audit log into DB: {exc}")
