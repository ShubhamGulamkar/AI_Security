from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.core.security import get_current_user

from app.security.encryption import encrypt_data

from app.services.document_service import create_document

from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)