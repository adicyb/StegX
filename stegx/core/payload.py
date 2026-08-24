import os
import struct

from stegx.core.crypto import encrypt_data


MAGIC = b"STEGX"
VERSION = 1

FLAG_ENCRYPTED = 0x01
SALT_SIZE = 16


def create_payload(
    file_path: str,
    password: str | None = None,
) -> bytes:
    """
    Read a file and package it into the StegX payload format.

    If a password is provided, the file data is encrypted
    before being added to the payload.
    """

    with open(file_path, "rb") as file:
        file_data = file.read()

    filename = os.path.basename(file_path)
    filename_bytes = filename.encode("utf-8")

    flags = 0
    salt = b""

    # Encrypt the file data if a password was provided.
    if password:
        salt, file_data = encrypt_data(
            file_data,
            password,
        )

        flags |= FLAG_ENCRYPTED

    header = b""

    # Magic signature: STEGX
    header += MAGIC

    # Version: 1 byte
    header += struct.pack("B", VERSION)

    # Flags: 1 byte
    header += struct.pack("B", flags)

    # Filename length: 2 bytes
    header += struct.pack(
        "H",
        len(filename_bytes),
    )

    # Filename
    header += filename_bytes

    # Payload length: 8 bytes
    header += struct.pack(
        "Q",
        len(file_data),
    )

    # If encrypted, store the salt before encrypted data.
    if flags & FLAG_ENCRYPTED:
        header += salt

    return header + file_data


def get_payload_info(payload: bytes) -> dict:
    """
    Read and validate a StegX payload header.
    """

    minimum_header_size = 5 + 1 + 1 + 2 + 8

    if len(payload) < minimum_header_size:
        raise ValueError(
            "Payload is too small to be a valid StegX payload."
        )

    offset = 0

    # Magic
    magic = payload[offset:offset + 5]
    offset += 5

    if magic != MAGIC:
        raise ValueError(
            "StegX signature not found."
        )

    # Version
    version = struct.unpack(
        "B",
        payload[offset:offset + 1],
    )[0]

    offset += 1

    # Flags
    flags = struct.unpack(
        "B",
        payload[offset:offset + 1],
    )[0]

    offset += 1

    # Filename length
    filename_length = struct.unpack(
        "H",
        payload[offset:offset + 2],
    )[0]

    offset += 2

    # Filename
    filename = payload[
        offset:offset + filename_length
    ].decode("utf-8")

    offset += filename_length

    # Payload length
    payload_size = struct.unpack(
        "Q",
        payload[offset:offset + 8],
    )[0]

    offset += 8

    encrypted = bool(
        flags & FLAG_ENCRYPTED
    )

    salt = None

    if encrypted:

        if len(payload) < offset + SALT_SIZE:
            raise ValueError(
                "Encrypted payload is missing salt."
            )

        salt = payload[
            offset:offset + SALT_SIZE
        ]

        offset += SALT_SIZE

    return {
        "magic": magic.decode(),
        "version": version,
        "encrypted": encrypted,
        "filename": filename,
        "payload_size": payload_size,
        "salt": salt,
        "header_size": offset,
    }