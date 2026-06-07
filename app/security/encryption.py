from cryptography.fernet import Fernet
from app.core.config import settings

print("=" * 60)
print("LOADING ENCRYPTION SERVICE")
print("=" * 60)

if not settings.ENCRYPTION_KEY:
    raise Exception(
        "ENCRYPTION_KEY not found in .env"
    )

cipher = Fernet(
    settings.ENCRYPTION_KEY.encode()
)

print("Encryption service initialized successfully")


def encrypt_data(data: bytes):

    print("=" * 60)
    print("ENCRYPTING DATA")
    print(f"Input Size: {len(data)} bytes")
    print("=" * 60)

    encrypted = cipher.encrypt(data)

    print(f"Encrypted Size: {len(encrypted)} bytes")

    return encrypted


def decrypt_data(data: bytes):

    print("=" * 60)
    print("DECRYPTING DATA")
    print(f"Encrypted Size: {len(data)} bytes")
    print("=" * 60)

    decrypted = cipher.decrypt(data)

    print(f"Decrypted Size: {len(decrypted)} bytes")

    return decrypted


# import os

# from cryptography.fernet import Fernet


# KEY_FILE = "aes.key"


# def load_or_create_key():

#     if not os.path.exists(KEY_FILE):

#         key = Fernet.generate_key()

#         with open(KEY_FILE, "wb") as f:
#             f.write(key)

#     with open(KEY_FILE, "rb") as f:
#         return f.read()


# cipher = Fernet(load_or_create_key())


# def encrypt_data(data: bytes):

#     return cipher.encrypt(data)


# def decrypt_data(data: bytes):

#     return cipher.decrypt(data)