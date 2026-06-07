from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException,UploadFile,File

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.auth import UserRegister
from app.schemas.auth import UserLogin

from app.services.auth_service import create_user
from app.services.auth_service import authenticate_user
from app.services.auth_service import get_user_by_username
from app.services.document_service import create_document,get_document

from app.core.security import create_access_token
from app.core.security import get_current_user
from fastapi.responses import StreamingResponse

import io
from app.security.hash_utils import generate_file_hash
from app.services.document_service import get_document_by_hash
from app.security.encryption import decrypt_data,encrypt_data
from app.services.audit_service import create_audit_log
from app.core.security import create_access_token
from app.core.security import create_refresh_token,decode_token
from fastapi import Header
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


@router.post("/register")
def register_user(
        payload: UserRegister,
        db: Session = Depends(get_db)
):

    existing = get_user_by_username(
        db,
        payload.username
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    user = create_user(
        db,
        payload.username,
        payload.email,
        payload.password,
        payload.role
    )

    create_audit_log(
        db,
        user.id,
        "REGISTER",
        f"User {user.username} registered"
    )

    return {
        "message": "User created"
    }



import uuid

# @router.post("/login")
# def login(
#         payload: UserLogin,
#         db: Session = Depends(get_db)
# ):

#     user = authenticate_user(
#         db,
#         payload.username,
#         payload.password
#     )

#     if not user:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid credentials"
#         )

#     access_token = create_access_token(
#         {
#             "sub": user.username,
#             "role": user.role,
#             "jti": str(uuid.uuid4())
#         }
#     )

#     refresh_token = create_refresh_token(
#         {
#             "sub": user.username,
#             "role": user.role,
#             "jti": str(uuid.uuid4())
#         }
#     )

#     create_audit_log(
#         db,
#         user.id,
#         "LOGIN",
#         f"{user.username} logged in"
#     )

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {
            "id": user.id,
            "sub": user.username,
            "role": user.role,
            "jti": str(uuid.uuid4())
        }
    )

    refresh_token = create_refresh_token(
        {
            "sub": user.username,
            "role": user.role,
            "jti": str(uuid.uuid4())
        }
    )

    create_audit_log(
        db=db,
        user_id=user.id,
        action="LOGIN",
        details=f"{user.username} logged in"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token_endpoint(refresh_token: str):

    payload = decode_token(
        refresh_token
    )

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    if payload.get("token_type") != "refresh":

        raise HTTPException(
            status_code=401,
            detail="Not a refresh token"
        )

    new_access_token = create_access_token(
        {
            "sub": payload["sub"],
            "role": payload["role"]
        }
    )

    return {
        "access_token": new_access_token
    }

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if current_user["role"] not in [
        "Doctor",
        "Admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )
    content = await file.read()

    file_hash = generate_file_hash(content)

    existing_document = get_document_by_hash(
        db,
        file_hash
    )

    if existing_document:

        raise HTTPException(
        status_code=409,
        detail="This document already exists in the system"
        )

    encrypted = encrypt_data(content)

    document = create_document(
        db,
        file.filename,
        encrypted,
        file_hash,
        current_user["id"]
    )

    create_audit_log(
        db,
        current_user["id"],
        "UPLOAD_DOCUMENT",
        f"Uploaded {file.filename}"
    )

    return {
        "message": "Document uploaded",
        "document_id": document.id
    }

@router.get("/{document_id}")
def download_document(
    document_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    document = get_document(
        db,
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    decrypted = decrypt_data(
        document.encrypted_data
    )

    create_audit_log(
        db,
        current_user["id"],
        "DOWNLOAD_DOCUMENT",
        f"Downloaded {document.filename}"
    )

    return StreamingResponse(
        io.BytesIO(decrypted),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename={document.filename}"
        }
    )