import os

import pytest

from stegx.core.payload import (
    MAGIC,
    VERSION,
    FLAG_ENCRYPTED,
    SALT_SIZE,
    create_payload,
    get_payload_info,
)


def test_create_normal_payload(tmp_path):
    """
    Test creation and parsing of a normal,
    non-encrypted StegX payload.
    """

    test_file = tmp_path / "secret.txt"

    test_content = b"Hello from StegX"

    test_file.write_bytes(test_content)

    payload = create_payload(
        str(test_file)
    )

    info = get_payload_info(payload)

    assert info["magic"] == MAGIC.decode()

    assert info["version"] == VERSION

    assert info["encrypted"] is False

    assert info["filename"] == "secret.txt"

    assert info["payload_size"] == len(
        test_content
    )

    extracted_data = payload[
        info["header_size"]:
    ]

    assert extracted_data == test_content


def test_create_encrypted_payload(tmp_path):
    """
    Test creation and parsing of an encrypted
    StegX payload.
    """

    test_file = tmp_path / "secret.txt"

    test_content = b"Hello from StegX"

    test_file.write_bytes(test_content)

    password = "mypassword123"

    payload = create_payload(
        str(test_file),
        password=password,
    )

    info = get_payload_info(payload)

    assert info["magic"] == MAGIC.decode()

    assert info["version"] == VERSION

    assert info["encrypted"] is True

    assert info["filename"] == "secret.txt"

    assert info["salt"] is not None

    assert len(
        info["salt"]
    ) == SALT_SIZE

    assert info["payload_size"] > 0


def test_encrypted_flag_is_set(tmp_path):
    """
    Verify that encrypted payloads contain
    the encryption flag.
    """

    test_file = tmp_path / "secret.txt"

    test_file.write_bytes(
        b"Test data"
    )

    payload = create_payload(
        str(test_file),
        password="password123",
    )

    # Payload layout:
    #
    # MAGIC = bytes 0-4
    # VERSION = byte 5
    # FLAGS = byte 6

    flags = payload[6]

    assert flags & FLAG_ENCRYPTED


def test_normal_payload_has_no_salt(tmp_path):
    """
    Verify that normal payloads do not contain
    encryption metadata.
    """

    test_file = tmp_path / "secret.txt"

    test_file.write_bytes(
        b"Normal payload"
    )

    payload = create_payload(
        str(test_file)
    )

    info = get_payload_info(payload)

    assert info["encrypted"] is False

    assert info["salt"] is None


def test_invalid_magic_raises_error():
    """
    A payload without the STEGX signature
    should not be accepted.
    """

    invalid_payload = (
        b"INVALID"
        + b"\x00" * 100
    )

    with pytest.raises(
        ValueError
    ):

        get_payload_info(
            invalid_payload
        )


def test_payload_too_small_raises_error():
    """
    Payloads smaller than the minimum header
    should raise an error.
    """

    with pytest.raises(
        ValueError
    ):

        get_payload_info(
            b"STEGX"
        )


def test_filename_is_preserved(tmp_path):
    """
    Verify that the original filename is
    correctly stored in the payload.
    """

    test_file = (
        tmp_path
        / "important_document.pdf"
    )

    test_file.write_bytes(
        b"Dummy PDF data"
    )

    payload = create_payload(
        str(test_file)
    )

    info = get_payload_info(payload)

    assert (
        info["filename"]
        == "important_document.pdf"
    )