from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog

from app.utils.mask_phi import mask_phi


def create_audit_log(
        db: Session,
        user_id: str,
        action: str,
        details: str
):

    log = AuditLog(
        user_id=user_id,
        action=action,
        details=mask_phi(details)
    )

    db.add(log)

    db.commit()