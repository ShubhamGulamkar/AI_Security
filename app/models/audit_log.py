import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import DateTime

from datetime import datetime

from app.db.database import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = Column(String)

    action = Column(String)

    details = Column(String)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )