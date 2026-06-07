import uuid

from sqlalchemy import Column
from sqlalchemy import String

from app.db.database import Base


class PHIMapping(Base):

    __tablename__ = "phi_mapping"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    document_id = Column(String)

    masked_value = Column(String)

    original_value = Column(String)