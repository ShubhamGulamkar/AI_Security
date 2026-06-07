import os

from cryptography.fernet import Fernet


KEY_FILE = "aes.key"


def load_or_create_key():

    if not os.path.exists(KEY_FILE):

        key = Fernet.generate_key()

        with open(KEY_FILE, "wb") as f:
            f.write(key)

    with open(KEY_FILE, "rb") as f:
        return f.read()


cipher = Fernet(load_or_create_key())


def encrypt_data(data: bytes):

    return cipher.encrypt(data)


def decrypt_data(data: bytes):

    return cipher.decrypt(data)