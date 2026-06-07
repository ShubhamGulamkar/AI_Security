from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from openai import OpenAI

from app.db.session import get_db
from app.models.document_chunk import DocumentChunk
from app.models.phi_mapping import PHIMapping

from app.security.encryption import decrypt_data
from app.security.phi_masking import unmask_phi
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

print("="*60)
print("RAG.PY LOADED")
print("="*60)

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)




@router.post("/summary/{document_id}")
def summarize_document(
    document_id: str,
    db: Session = Depends(get_db)
):

    client = OpenAI()

    chunks = db.query(
        DocumentChunk
    ).filter(
        DocumentChunk.document_id == document_id
    ).all()

    if not chunks:
        return {
            "error": "No chunks found"
        }

    context = "\n".join(
        chunk.chunk_text
        for chunk in chunks
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {
            "role": "system",
            "content": """
            You are a healthcare document summarization assistant.

            Generate a clean, readable summary.

            Keep it professional and easy for doctors to read.
            """
        },
        {
            "role": "user",
            "content": context
        }
    ],
    temperature=0
    )

    summary = response.choices[0].message.content

    rows = db.query(
        PHIMapping
    ).filter(
        PHIMapping.document_id == document_id
    ).all()

    mappings = {}

    for row in rows:

        original = decrypt_data(
            row.original_value
        ).decode()

        mappings[row.masked_value] = original

    final_summary = unmask_phi(
        summary,
        mappings
    )

    return {
        "document_id": document_id,
        "summary": final_summary
    }


# @router.get(
#     "/summary/{document_id}"
# )
# def summarize_document(
#     document_id: str,
#     db: Session = Depends(get_db)
# ):

#     chunks = db.query(
#         DocumentChunk
#     ).filter(
#         DocumentChunk.document_id
#         == document_id
#     ).all()

#     context = "\n".join(
#     chunk.chunk_text
#     for chunk in chunks
#     )

# from openai import OpenAI

# client = OpenAI()

# response = client.chat.completions.create(
#     model="gpt-4o",
#     messages=[
#         {
#             "role":"system",
#             "content":
#             """
#             Summarize medical document.
#             """
#         },
#         {
#             "role":"user",
#             "content":context
#         }
#     ]
# )

# summary = response.choices[
#     0
# ].message.content

# rows = db.query(
#     PHIMapping
# ).filter(
#     PHIMapping.document_id
#     == document_id
# ).all()

# mappings = {}

# for row in rows:

#     original = decrypt_data(
#         row.original_value
#     ).decode()

#     mappings[
#         row.masked_value
#     ] = original

# final_summary = unmask_phi(
#     summary,
#     mappings
# )

# return {
#     "document_id": document_id,
#     "summary": final_summary
# }