import uuid

from sqlalchemy import Column
from sqlalchemy import String

from app.db.database import Base


class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    document_id = Column(String)

    chunk_text = Column(String)