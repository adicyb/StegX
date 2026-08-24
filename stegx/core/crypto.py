import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


SALT_SIZE = 16
ITERATIONS = 600_000


def derive_key(password: str, salt: bytes) -> bytes:
    """
    Derive a Fernet-compatible encryption key from
    a user password and salt.
    """

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )

    key = base64.urlsafe_b64encode(
        kdf.derive(password.encode("utf-8"))
    )

    return key


def encrypt_data(
    data: bytes,
    password: str,
) -> tuple[bytes, bytes]:
    """
    Encrypt raw data using a password.

    Returns:
        salt, encrypted_data
    """

    salt = os.urandom(SALT_SIZE)

    key = derive_key(
        password,
        salt,
    )

    cipher = Fernet(key)

    encrypted_data = cipher.encrypt(data)

    return salt, encrypted_data


def decrypt_data(
    encrypted_data: bytes,
    password: str,
    salt: bytes,
) -> bytes:
    """
    Decrypt encrypted data using the password and salt.
    """

    key = derive_key(
        password,
        salt,
    )

    cipher = Fernet(key)

    try:
        return cipher.decrypt(encrypted_data)

    except InvalidToken:
        raise ValueError(
            "Incorrect password or corrupted encrypted data."
        )