import fitz  # PyMuPDF
import io


def extract_text_from_pdf_bytes(
        pdf_bytes: bytes
):

    text = ""

    pdf = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    for page in pdf:

        text += page.get_text()

    pdf.close()

    return text