import hashlib


def generate_file_hash(content: bytes):

    return hashlib.sha256(
        content
    ).hexdigest()