import cv2
import numpy as np

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


def analyze_video_signature(
    video_path: str,
    position_key: str | None = None,
) -> dict:
    """
    Check whether a video contains a valid
    StegX payload signature.

    If a position key is supplied, the signature
    is recovered from deterministic randomized
    embedding positions.
    """

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():

        raise ValueError(
            "Could not open the video."
        )

    width = int(
        video.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    frame_count = int(
        video.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    video.release()

    frame_values = (
        width
        * height
        * 3
    )

    available_bits = (
        frame_values
        * frame_count
    )

    # ------------------------------------------------
    # RANDOMIZED SIGNATURE EXTRACTION
    # ------------------------------------------------

    if position_key:

        # We first recover enough bits for the
        # minimum possible StegX header.
        #
        # 5 magic
        # 1 version
        # 1 flags
        # 2 filename length
        # 8 payload length
        minimum_bits = (
            5
            + 1
            + 1
            + 2
            + 8
        ) * 8

        positions = generate_positions(
            available_bits,
            minimum_bits,
            position_key,
        )

        recovered_bits = [0] * minimum_bits

        positions_by_frame = {}

        for payload_bit_index, global_position in enumerate(
            positions
        ):

            frame_index = (
                global_position // frame_values
            )

            local_position = (
                global_position % frame_values
            )

            if frame_index not in positions_by_frame:

                positions_by_frame[
                    frame_index
                ] = []

            positions_by_frame[
                frame_index
            ].append(
                (
                    local_position,
                    payload_bit_index,
                )
            )

        video = cv2.VideoCapture(video_path)

        frame_index = 0

        while True:

            success, frame = video.read()

            if not success:
                break

            if frame_index in positions_by_frame:

                flat_frame = frame.reshape(-1)

                for (
                    local_position,
                    payload_bit_index,
                ) in positions_by_frame[
                    frame_index
                ]:

                    recovered_bits[
                        payload_bit_index
                    ] = int(
                        flat_frame[
                            local_position
                        ] & 1
                    )

            frame_index += 1

        video.release()

        recovered_bytes = bits_to_bytes(
            recovered_bits
        )

        # Check magic.
        if recovered_bytes[:5] != MAGIC:

            return {
                "detected": False
            }

        # Filename length.
        filename_length = int.from_bytes(
            recovered_bytes[7:9],
            byteorder="little",
        )

        # Calculate full header size.
        header_size = (
            5
            + 1
            + 1
            + 2
            + filename_length
            + 8
        )

        # If encrypted, add the 16-byte salt.
        flags = recovered_bytes[6]

        if flags & 0x01:

            header_size += 16

        required_bits = (
            header_size * 8
        )

        # Generate positions again for the complete
        # header.
        positions = generate_positions(
            available_bits,
            required_bits,
            position_key,
        )

        recovered_bits = [0] * required_bits

        positions_by_frame = {}

        for payload_bit_index, global_position in enumerate(
            positions
        ):

            frame_index = (
                global_position // frame_values
            )

            local_position = (
                global_position % frame_values
            )

            if frame_index not in positions_by_frame:

                positions_by_frame[
                    frame_index
                ] = []

            positions_by_frame[
                frame_index
            ].append(
                (
                    local_position,
                    payload_bit_index,
                )
            )

        video = cv2.VideoCapture(video_path)

        frame_index = 0

        while True:

            success, frame = video.read()

            if not success:
                break

            if frame_index in positions_by_frame:

                flat_frame = frame.reshape(-1)

                for (
                    local_position,
                    payload_bit_index,
                ) in positions_by_frame[
                    frame_index
                ]:

                    recovered_bits[
                        payload_bit_index
                    ] = int(
                        flat_frame[
                            local_position
                        ] & 1
                    )

            frame_index += 1

        video.release()

        recovered_bytes = bits_to_bytes(
            recovered_bits
        )

        try:

            info = get_payload_info(
                recovered_bytes
            )

            return {
                "detected": True,
                "version": info["version"],
                "encrypted": info["encrypted"],
                "filename": info["filename"],
                "payload_size": info["payload_size"],
                "randomized": True,
            }

        except Exception:

            return {
                "detected": False
            }

    # ------------------------------------------------
    # SEQUENTIAL SIGNATURE EXTRACTION
    # ------------------------------------------------

    video = cv2.VideoCapture(video_path)

    recovered_bits = []

    while True:

        success, frame = video.read()

        if not success:
            break

        flat_frame = frame.reshape(-1)

        frame_bits = (
            flat_frame & 1
        )

        recovered_bits.extend(
            frame_bits.tolist()
        )

        if len(recovered_bits) >= 40:

            recovered_bytes = bits_to_bytes(
                recovered_bits[:40]
            )

            if recovered_bytes[:5] != MAGIC:

                video.release()

                return {
                    "detected": False
                }

            break

    video.release()

    if len(recovered_bits) < 40:

        return {
            "detected": False
        }

    recovered_bytes = bits_to_bytes(
        recovered_bits
    )

    if len(recovered_bytes) < 9:

        return {
            "detected": False
        }

    filename_length = int.from_bytes(
        recovered_bytes[7:9],
        byteorder="little",
    )

    header_size = (
        5
        + 1
        + 1
        + 2
        + filename_length
        + 8
    )

    flags = recovered_bytes[6]

    if flags & 0x01:

        header_size += 16

    required_bits = (
        header_size * 8
    )

    video = cv2.VideoCapture(video_path)

    recovered_bits = []

    while True:

        success, frame = video.read()

        if not success:
            break

        flat_frame = frame.reshape(-1)

        frame_bits = (
            flat_frame & 1
        )

        recovered_bits.extend(
            frame_bits.tolist()
        )

        if len(recovered_bits) >= required_bits:
            break

    video.release()

    recovered_bytes = bits_to_bytes(
        recovered_bits[:required_bits]
    )

    try:

        info = get_payload_info(
            recovered_bytes
        )

        return {
            "detected": True,
            "version": info["version"],
            "encrypted": info["encrypted"],
            "filename": info["filename"],
            "payload_size": info["payload_size"],
            "randomized": False,
        }

    except Exception:

        return {
            "detected": False
        }