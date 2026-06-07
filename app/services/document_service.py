from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    filename: str,
    encrypted_data: bytes,
    file_hash,
    uploaded_by: int
):

    document = Document(
        filename=filename,
        encrypted_data=encrypted_data,
        file_hash=file_hash,
        uploaded_by=uploaded_by
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    return document


def get_document(
    db: Session,
    document_id: str
):
    return db.query(Document).filter(
        Document.id == document_id
    ).first()

def get_document_by_hash(
    db,
    file_hash: str
):

    return db.query(Document).filter(
        Document.file_hash == file_hash
    ).first()