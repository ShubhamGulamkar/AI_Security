import re


def mask_phi(text: str):

    if not text:
        return text

    text = re.sub(
        r"\b\d{10}\b",
        "[PHONE]",
        text
    )

    text = re.sub(
        r"\b\d{3}-\d{2}-\d{4}\b",
        "[SSN]",
        text
    )

    return text