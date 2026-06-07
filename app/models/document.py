import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import LargeBinary
from sqlalchemy import DateTime

from datetime import datetime

from app.db.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    filename = Column(String)

    encrypted_data = Column(
        LargeBinary
    )

    uploaded_by = Column(String)

    file_hash = Column(
        String,
        unique=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )