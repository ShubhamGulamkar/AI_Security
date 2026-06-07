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

from app.models.phi_mapping import PHIMapping

import io
from app.security.hash_utils import generate_file_hash
from app.services.document_service import get_document_by_hash
from app.security.encryption import decrypt_data,encrypt_data
from app.services.audit_service import create_audit_log
from app.services.embedding_service import generate_embedding
from app.core.security import create_access_token
from app.security.phi_masking import mask_phi
from app.services.chunk_service import create_chunks
from app.models.document_chunk import DocumentChunk
from app.services.faiss_service import add_chunk
from app.core.security import create_refresh_token,decode_token
from app.utils.pdf_utils import (
    extract_text_from_pdf_bytes
)
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

# @router.post("/upload")
# async def upload_document(
#     file: UploadFile = File(...),
#     current_user=Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):

#     if current_user["role"] not in [
#         "Doctor",
#         "Admin"
#     ]:
#         raise HTTPException(
#             status_code=403,
#             detail="Access denied"
#         )
#     content = await file.read()

#     file_hash = generate_file_hash(content)

#     existing_document = get_document_by_hash(
#         db,
#         file_hash
#     )

#     if existing_document:

#         raise HTTPException(
#         status_code=409,
#         detail="This document already exists in the system"
#         )

#     encrypted = encrypt_data(content)

#     document = create_document(
#         db,
#         file.filename,
#         encrypted,
#         file_hash,
#         current_user["id"]
#     )
#     # Extract PDF text
#     text = extract_text_from_pdf_bytes(content)

#     # Mask PHI
#     masked_text, mappings = mask_phi(text)

#     # Chunk document
#     chunks = create_chunks(masked_text)
#     print("=" * 50)
#     print("TEXT LENGTH:", len(text))
#     print("MASKED TEXT LENGTH:", len(masked_text))
#     print("TOTAL CHUNKS:", len(chunks))
#     print("=" * 50)

#     # Store PHI mappings
#     for token, original in mappings.items():

#         mapping_row = PHIMapping(
#             document_id=document.id,
#             masked_value=token,
#             original_value=encrypt_data(
#                 original.encode()
#             )
#         )

#         db.add(mapping_row)

#     db.commit()

#     for chunk in chunks:

#         embedding = generate_embedding(
#             chunk
#         )

#         add_chunk(
#             embedding,
#             chunk
#         )

#         db.add(
#             DocumentChunk(
#                 document_id=document.id,
#                 chunk_text=chunk
#             )
#         )

#     db.commit()


#     create_audit_log(
#         db,
#         current_user["id"],
#         "UPLOAD_DOCUMENT",
#         f"Uploaded {file.filename}"
#     )

#     return {
#         "message": "Document uploaded",
#         "document_id": document.id
#     }

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    print("\n" + "=" * 80)
    print("UPLOAD STARTED")
    print("=" * 80)

    if current_user["role"] not in [
        "Doctor",
        "Admin"
    ]:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    try:

        content = await file.read()

        print(f"File Name: {file.filename}")
        print(f"File Size: {len(content)} bytes")

        file_hash = generate_file_hash(content)

        print(f"File Hash: {file_hash}")

        existing_document = get_document_by_hash(
            db,
            file_hash
        )

        if existing_document:

            print("Duplicate document detected")

            raise HTTPException(
                status_code=409,
                detail="This document already exists in the system"
            )

        # ---------------------------------------------------
        # Encrypt & Save Document
        # ---------------------------------------------------

        encrypted = encrypt_data(content)

        document = create_document(
            db,
            file.filename,
            encrypted,
            file_hash,
            current_user["id"]
        )

        print(f"Document Saved")
        print(f"Document ID: {document.id}")

        # ---------------------------------------------------
        # Extract Text
        # ---------------------------------------------------

        print("\nEXTRACTING PDF TEXT...")

        text = extract_text_from_pdf_bytes(
            content
        )

        print(f"Extracted Text Length: {len(text)}")

        print("\nFIRST 500 CHARACTERS:")
        print(text[:500])

        if not text.strip():

            print("WARNING: NO TEXT EXTRACTED FROM PDF")

            return {
                "message": "PDF uploaded but no text extracted",
                "document_id": document.id
            }

        # ---------------------------------------------------
        # PHI Masking
        # ---------------------------------------------------

        print("\nMASKING PHI...")

        masked_text, mappings = mask_phi(
            text
        )

        print(f"Masked Text Length: {len(masked_text)}")
        print(f"Total PHI Mappings: {len(mappings)}")

        print("\nFIRST 500 MASKED CHARS:")
        print(masked_text[:500])

        # ---------------------------------------------------
        # Chunking
        # ---------------------------------------------------

        print("\nCREATING CHUNKS...")

        chunks = create_chunks(
            masked_text
        )

        print(f"Total Chunks Created: {len(chunks)}")

        if len(chunks) == 0:

            print("WARNING: NO CHUNKS GENERATED")

            return {
                "message": "No chunks generated",
                "document_id": document.id
            }

        # ---------------------------------------------------
        # Store PHI Mapping
        # ---------------------------------------------------

        print("\nSAVING PHI MAPPINGS...")

        for token, original in mappings.items():

            mapping_row = PHIMapping(
                document_id=document.id,
                masked_value=token,
                original_value=encrypt_data(
                    original.encode()
                )
            )

            db.add(mapping_row)

        try:

            db.commit()

            print(
                f"PHI Mappings Saved: {len(mappings)}"
            )

        except Exception as e:

            db.rollback()

            print(
                f"PHI Mapping Save Failed: {str(e)}"
            )

            raise

        # ---------------------------------------------------
        # Save Chunks
        # ---------------------------------------------------

        print("\nPROCESSING CHUNKS...")

        for idx, chunk in enumerate(chunks):

            print(
                f"\nChunk {idx+1}/{len(chunks)}"
            )

            print(
                f"Chunk Length: {len(chunk)}"
            )

            print(
                f"Chunk Preview: {chunk[:100]}"
            )

            # Generate Embedding

            embedding = generate_embedding(
                chunk
            )

            print(
                f"Embedding Length: {len(embedding)}"
            )

            # Save to FAISS

            add_chunk(
                embedding,
                chunk
            )

            # Save to Database

            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_text=chunk
                )
            )

        print("\nCOMMITTING CHUNKS TO DATABASE...")

        try:

            db.commit()

            print(
                "DOCUMENT CHUNKS SAVED SUCCESSFULLY"
            )

        except Exception as e:

            db.rollback()

            print(
                f"CHUNK SAVE FAILED: {str(e)}"
            )

            raise

        # ---------------------------------------------------
        # Verify Chunks Saved
        # ---------------------------------------------------

        saved_chunks = db.query(
            DocumentChunk
        ).filter(
            DocumentChunk.document_id
            == document.id
        ).count()

        print(
            f"TOTAL CHUNKS IN DB: {saved_chunks}"
        )

        # ---------------------------------------------------
        # Audit Log
        # ---------------------------------------------------

        create_audit_log(
            db,
            current_user["id"],
            "UPLOAD_DOCUMENT",
            f"Uploaded {file.filename}"
        )

        print("\nUPLOAD COMPLETED SUCCESSFULLY")
        print("=" * 80)

        return {
            "message": "Document uploaded successfully",
            "document_id": document.id,
            "chunks_saved": saved_chunks,
            "phi_mappings": len(mappings)
        }

    except Exception as e:

        print("\nUPLOAD FAILED")
        print(str(e))
        print("=" * 80)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

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

