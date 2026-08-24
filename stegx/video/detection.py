import cv2

from stegx.core.payload import (
    MAGIC,
    get_payload_info,
)


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
) -> dict:
    """
    Check whether a video contains a valid
    StegX payload signature.
    """

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():

        raise ValueError(
            "Could not open the video."
        )

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

        # We only need enough bytes to check
        # the STEGX signature first.
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

    # ------------------------------------------------
    # We found the STEGX magic.
    # Now recover enough data to parse the header.
    # ------------------------------------------------

    recovered_bytes = bits_to_bytes(
        recovered_bits
    )

    if len(recovered_bytes) < 9:

        return {
            "detected": False
        }

    # Filename length is stored at bytes 7-8.
    filename_length = int.from_bytes(
        recovered_bytes[7:9],
        byteorder="little",
    )

    basic_header_size = (
        5   # Magic
        + 1 # Version
        + 1 # Flags
        + 2 # Filename length
        + filename_length
        + 8 # Payload length
    )

    required_bytes = basic_header_size

    # Continue reading frames until we have
    # the complete header.
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

        if len(recovered_bits) >= required_bytes * 8:
            break

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
        }

    except Exception:

        return {
            "detected": False
        }