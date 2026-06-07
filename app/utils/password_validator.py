import re

from fastapi import HTTPException


def validate_password(password: str):

    if len(password) < 12:

        raise HTTPException(
            status_code=400,
            detail="Password must be at least 12 characters"
        )

    if not re.search(r"[A-Z]", password):

        raise HTTPException(
            status_code=400,
            detail="Password must contain uppercase letter"
        )

    if not re.search(r"[a-z]", password):

        raise HTTPException(
            status_code=400,
            detail="Password must contain lowercase letter"
        )

    if not re.search(r"\d", password):

        raise HTTPException(
            status_code=400,
            detail="Password must contain number"
        )

    if not re.search(
        r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]",
        password
    ):

        raise HTTPException(
            status_code=400,
            detail="Password must contain special character"
        )

    return True