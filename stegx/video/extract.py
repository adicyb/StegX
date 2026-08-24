import os
import struct

import cv2
import numpy as np

from stegx.core.payload import (
    MAGIC,
    get_payload_info,
)
from stegx.core.crypto import decrypt_data


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
            value = (value << 1) | bit

        output.append(value)

    return bytes(output)


def extract_video_payload(
    video_path: str,
    output_directory: str,
    password: str | None = None,
):
    """
    Extract a StegX payload from a video.
    """

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise ValueError(
            "Could not open the video."
        )

    recovered_bits = []

    filename_length = None
    header_size = None
    payload_size = None
    total_payload_bits = None

    while True:

        success, frame = video.read()

        if not success:
            break

        flat_frame = frame.reshape(-1)

        frame_bits = (
            flat_frame & 1
        ).astype(np.uint8)

        recovered_bits.extend(
            frame_bits.tolist()
        )

        recovered_bytes = bits_to_bytes(
            recovered_bits
        )

        # ------------------------------------------------
        # STEP 1: Verify STEGX magic.
        # ------------------------------------------------

        if len(recovered_bytes) >= 5:

            magic = recovered_bytes[:5]

            if magic != MAGIC:

                video.release()

                raise ValueError(
                    "No valid STEGX payload found "
                    "in this video."
                )

        else:
            continue

        # ------------------------------------------------
        # STEP 2: Read filename length.
        #
        # Structure:
        #
        # MAGIC          5 bytes
        # VERSION        1 byte
        # FLAGS          1 byte
        # FILENAME LEN   2 bytes
        # ------------------------------------------------

        if (
            filename_length is None
            and len(recovered_bytes) >= 9
        ):

            filename_length = struct.unpack(
                "H",
                recovered_bytes[7:9]
            )[0]

            # Full header size:
            #
            # 5 magic
            # 1 version
            # 1 flags
            # 2 filename length
            # filename bytes
            # 8 payload length

            header_size = (
                5
                + 1
                + 1
                + 2
                + filename_length
                + 8
            )

        # ------------------------------------------------
        # STEP 3: Once the complete header exists,
        # read the payload size.
        # ------------------------------------------------

        if (
            header_size is not None
            and payload_size is None
            and len(recovered_bytes) >= header_size
        ):

            payload_size_offset = (
                header_size - 8
            )

            payload_size = struct.unpack(
                "Q",
                recovered_bytes[
                    payload_size_offset:
                    header_size
                ]
            )[0]

            # Read the flags byte.
            # Layout:
            # MAGIC   = bytes 0-4
            # VERSION = byte 5
            # FLAGS   = byte 6
            flags = recovered_bytes[6]

            encrypted = bool(flags & 0x01)

            total_payload_bytes = (
                header_size
                + payload_size
            )

            # Encrypted payloads contain an additional
            # 16-byte salt between the header and
            # encrypted data.
            if encrypted:

                total_payload_bytes += 16

            total_payload_bits = (
                total_payload_bytes * 8
            )

        # ------------------------------------------------
        # STEP 4: Stop as soon as we have the
        # complete payload.
        # ------------------------------------------------

        if (
            total_payload_bits is not None
            and len(recovered_bits)
            >= total_payload_bits
        ):
            break

    video.release()

    if total_payload_bits is None:

        raise ValueError(
            "Could not recover a valid "
            "STEGX payload header."
        )

    if len(recovered_bits) < total_payload_bits:

        raise ValueError(
            "Video ended before the complete "
            "payload could be recovered."
        )

    # Recover only the exact payload.
    payload = bits_to_bytes(
        recovered_bits[:total_payload_bits]
    )

    # Parse the complete payload.
    payload_info = get_payload_info(
        payload
    )

    header_size = payload_info[
        "header_size"
    ]

    payload_data = payload[
        header_size:
        header_size + payload_info[
            "payload_size"
        ]
    ]

    filename = payload_info[
        "filename"
    ]

    encrypted = payload_info[
        "encrypted"
    ]

    # ------------------------------------------------
    # STEP 5: Decrypt if necessary.
    # ------------------------------------------------

    if encrypted:

        if password is None or password == "":

            raise ValueError(
                "This payload is encrypted. "
                "A password is required."
            )

        salt = payload_info["salt"]

        payload_data = decrypt_data(
            payload_data,
            password,
            salt,
        )

    # ------------------------------------------------
    # STEP 6: Save recovered file.
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
        "wb"
    ) as file:

        file.write(
            payload_data
        )

    return {
        "filename": filename,
        "payload_size": len(
            payload_data
        ),
        "encrypted": encrypted,
        "output_path": output_path,
    }