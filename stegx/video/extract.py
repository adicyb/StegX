import os

import cv2
import numpy as np

from stegx.core.crypto import decrypt_data
from stegx.core.payload import (
    MAGIC,
    get_payload_info,
)
from stegx.core.positions import generate_positions


def bits_to_bytes(bits: list[int]) -> bytes:
    """
    Convert a list of bits into bytes.
    """

    output = bytearray()

    for index in range(0, len(bits), 8):

        byte_bits = bits[index:index + 8]

        if len(byte_bits) < 8:
            break

        value = 0

        for bit in byte_bits:

            value = (
                value << 1
            ) | bit

        output.append(value)

    return bytes(output)


def get_video_channel_values(
    video_path: str,
) -> np.ndarray:
    """
    Read every video frame and return all BGR
    channel values as one continuous array.
    """

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():

        raise ValueError(
            "Could not open the video."
        )

    values = []

    while True:

        success, frame = video.read()

        if not success:
            break

        values.append(
            frame.reshape(-1)
        )

    video.release()

    if not values:

        raise ValueError(
            "No frames could be read from the video."
        )

    return np.concatenate(values)


def extract_video_payload(
    video_path: str,
    output_directory: str,
    password: str | None = None,
    position_key: str | None = None,
):
    """
    Extract a StegX payload from a video.

    Supports both sequential embedding and
    deterministic randomized embedding positions.
    """

    channel_values = get_video_channel_values(
        video_path
    )

    total_positions = len(
        channel_values
    )

    # ------------------------------------------------
    # STEP 1: Recover enough data to read the header.
    # ------------------------------------------------

    if position_key:

        # We first need enough randomized positions
        # to recover the minimum possible header.
        #
        # Minimum structure:
        #
        # MAGIC          5 bytes
        # VERSION        1 byte
        # FLAGS          1 byte
        # FILENAME LEN   2 bytes
        # PAYLOAD LEN    8 bytes
        #
        # Total = 17 bytes minimum.
        initial_bits = 17 * 8

        positions = generate_positions(
            total_positions,
            initial_bits,
            position_key,
        )

        initial_bits_data = (
            channel_values[positions] & 1
        ).astype(
            np.uint8
        ).tolist()

    else:

        initial_bits_data = (
            channel_values[:17 * 8] & 1
        ).astype(
            np.uint8
        ).tolist()

    initial_data = bits_to_bytes(
        initial_bits_data
    )

    # ------------------------------------------------
    # STEP 2: Validate MAGIC.
    # ------------------------------------------------

    if initial_data[:len(MAGIC)] != MAGIC:

        if position_key:

            raise ValueError(
                "No valid StegX payload signature found. "
                "The position key may be incorrect."
            )

        raise ValueError(
            "No valid StegX payload found "
            "in this video."
        )

    # ------------------------------------------------
    # STEP 3: Read filename length.
    # ------------------------------------------------

    filename_length = int.from_bytes(
        initial_data[7:9],
        byteorder="little",
    )

    # Base header:
    #
    # MAGIC          5
    # VERSION        1
    # FLAGS          1
    # FILENAME LEN   2
    # FILENAME       variable
    # PAYLOAD LEN    8

    base_header_size = (
        5
        + 1
        + 1
        + 2
        + filename_length
        + 8
    )

    header_bits_required = (
        base_header_size * 8
    )

    # ------------------------------------------------
    # STEP 4: Recover complete base header.
    # ------------------------------------------------

    if position_key:

        positions = generate_positions(
            total_positions,
            header_bits_required,
            position_key,
        )

        header_bits = (
            channel_values[positions] & 1
        ).astype(
            np.uint8
        ).tolist()

    else:

        header_bits = (
            channel_values[
                :header_bits_required
            ] & 1
        ).astype(
            np.uint8
        ).tolist()

    base_header = bits_to_bytes(
        header_bits
    )

    # ------------------------------------------------
    # STEP 5: Read encryption flag and payload size.
    # ------------------------------------------------

    flags = base_header[6]

    encrypted = bool(
        flags & 0x01
    )

    payload_size = int.from_bytes(
        base_header[-8:],
        byteorder="little",
    )

    # Salt is part of the stored header when encrypted.
    salt_size = 16 if encrypted else 0

    total_payload_bytes = (
        base_header_size
        + salt_size
        + payload_size
    )

    total_payload_bits = (
        total_payload_bytes * 8
    )

    if total_payload_bits > total_positions:

        raise ValueError(
            "Payload size exceeds available "
            "video data."
        )

    # ------------------------------------------------
    # STEP 6: Recover complete payload.
    # ------------------------------------------------

    if position_key:

        positions = generate_positions(
            total_positions,
            total_payload_bits,
            position_key,
        )

        recovered_bits = (
            channel_values[positions] & 1
        ).astype(
            np.uint8
        ).tolist()

    else:

        recovered_bits = (
            channel_values[
                :total_payload_bits
            ] & 1
        ).astype(
            np.uint8
        ).tolist()

    payload = bits_to_bytes(
        recovered_bits
    )

    # ------------------------------------------------
    # STEP 7: Parse using the central payload parser.
    # ------------------------------------------------

    try:

        payload_info = get_payload_info(
            payload
        )

    except Exception:

        if position_key:

            raise ValueError(
                "Could not parse the StegX payload. "
                "The position key may be incorrect."
            )

        raise ValueError(
            "Could not parse the StegX payload."
        )

    header_size = (
        payload_info["header_size"]
    )

    payload_size = (
        payload_info["payload_size"]
    )

    payload_data = payload[
        header_size:
        header_size + payload_size
    ]

    if len(payload_data) != payload_size:

        raise ValueError(
            "Payload appears to be incomplete "
            "or corrupted."
        )

    filename = (
        payload_info["filename"]
    )

    encrypted = (
        payload_info["encrypted"]
    )

    # ------------------------------------------------
    # STEP 8: Decrypt encrypted payload.
    # ------------------------------------------------

    if encrypted:

        if not password:

            raise ValueError(
                "This payload is encrypted. "
                "A password is required."
            )

        payload_data = decrypt_data(
            payload_data,
            password,
            payload_info["salt"],
        )

    # ------------------------------------------------
    # STEP 9: Save recovered file.
    # ------------------------------------------------

    os.makedirs(
        output_directory,
        exist_ok=True,
    )

    output_path = os.path.join(
        output_directory,
        filename,
    )

    with open(
        output_path,
        "wb",
    ) as file:

        file.write(
            payload_data
        )

    return {
    "filename": filename,
    "payload_size": len(payload_data),
    "encrypted": encrypted,
    "randomized": bool(position_key),
    "output_path": output_path,
}