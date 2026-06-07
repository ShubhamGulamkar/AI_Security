from fastapi import FastAPI

from app.core.config import settings

from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.models.document import Document
from app.api.document import router as document_router

from app.api.rag import router as rag_router

app = FastAPI(
    title=settings.APP_NAME
)

app.include_router(document_router)

app.include_router(auth_router)

app.include_router(user_router)

app.include_router(rag_router)


@app.get("/")
def root():

    return {
        "message": "Medical Secure RAG API"
    }