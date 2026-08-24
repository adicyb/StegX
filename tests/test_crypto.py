import pytest

from stegx.core.crypto import (
    decrypt_data,
    encrypt_data,
)


def test_encrypt_and_decrypt():

    original_data = (
        b"Hello from StegX encryption test"
    )

    password = "testpassword123"

    salt, encrypted_data = encrypt_data(
        original_data,
        password,
    )

    decrypted_data = decrypt_data(
        encrypted_data,
        password,
        salt,
    )

    assert decrypted_data == original_data


def test_encrypted_data_is_different():

    original_data = (
        b"Sensitive StegX data"
    )

    password = "testpassword123"

    salt, encrypted_data = encrypt_data(
        original_data,
        password,
    )

    assert encrypted_data != original_data


def test_wrong_password_raises_error():

    original_data = (
        b"Secret StegX message"
    )

    salt, encrypted_data = encrypt_data(
        original_data,
        "correctpassword",
    )

    with pytest.raises(ValueError):

        decrypt_data(
            encrypted_data,
            "wrongpassword",
            salt,
        )


def test_encryption_generates_salt():

    original_data = b"Test data"

    salt, encrypted_data = encrypt_data(
        original_data,
        "password123",
    )

    assert isinstance(salt, bytes)
    assert len(salt) == 16
    assert len(encrypted_data) > 0