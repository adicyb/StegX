import cv2
import numpy as np

from stegx.core.payload import create_payload
from stegx.core.positions import generate_positions


def bytes_to_bits(data: bytes) -> str:
    """
    Convert bytes into a continuous string of bits.
    """

    return "".join(
        format(byte, "08b")
        for byte in data
    )


def embed_video_payload(
    video_path: str,
    payload_path: str,
    output_path: str,
    password: str | None = None,
    position_key: str | None = None,
):
    """
    Embed a StegX payload into a video using
    1-bit LSB steganography across BGR channels.

    If a position key is provided, payload bits are
    embedded into deterministic randomized positions.

    The output video uses the FFV1 lossless codec
    to preserve the embedded LSB data.
    """

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise ValueError(
            "Could not open the input video."
        )

    width = int(
        video.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    fps = video.get(
        cv2.CAP_PROP_FPS
    )

    frame_count = int(
        video.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    # Create the StegX payload.
    payload = create_payload(
        payload_path,
        password=password,
    )

    payload_bits = bytes_to_bits(payload)

    required_bits = len(payload_bits)

    # Total BGR channel values across the video.
    available_bits = (
        width
        * height
        * 3
        * frame_count
    )

    if required_bits > available_bits:

        video.release()

        raise ValueError(
            "Payload is too large for this video. "
            f"Required: {required_bits:,} bits, "
            f"Available: {available_bits:,} bits."
        )

    # Generate randomized global positions.
    positions = None

    if position_key:

        positions = generate_positions(
            available_bits,
            required_bits,
            position_key,
        )

    fourcc = cv2.VideoWriter_fourcc(
        *"FFV1"
    )

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height),
    )

    if not writer.isOpened():

        video.release()

        raise ValueError(
            "Could not create output video "
            "using FFV1 codec."
        )

    bit_index = 0
    frames_processed = 0

    frame_values = (
        width
        * height
        * 3
    )

    # ------------------------------------------------
    # Prepare randomized positions by frame.
    #
    # Each entry stores:
    #
    # frame_index:
    # [
    #     (local_channel_position, payload_bit_index),
    #     ...
    # ]
    # ------------------------------------------------

    positions_by_frame = {}

    if positions is not None:

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

    while True:

        success, frame = video.read()

        if not success:
            break

        flat_frame = frame.reshape(-1)

        # ------------------------------------------------
        # SEQUENTIAL EMBEDDING
        # ------------------------------------------------

        if (
            position_key is None
            and bit_index < required_bits
        ):

            remaining_bits = (
                required_bits - bit_index
            )

            usable_values = min(
                remaining_bits,
                len(flat_frame),
            )

            bits = np.fromiter(
                (
                    int(bit)
                    for bit in payload_bits[
                        bit_index:
                        bit_index + usable_values
                    ]
                ),
                dtype=np.uint8,
                count=usable_values,
            )

            flat_frame[:usable_values] &= (
                0b11111110
            )

            flat_frame[:usable_values] |= bits

            bit_index += usable_values

        # ------------------------------------------------
        # RANDOMIZED EMBEDDING
        # ------------------------------------------------

        elif position_key is not None:

            if frames_processed in positions_by_frame:

                for (
                    local_position,
                    payload_bit_index,
                ) in positions_by_frame[
                    frames_processed
                ]:

                    bit = int(
                        payload_bits[
                            payload_bit_index
                        ]
                    )

                    flat_frame[local_position] = (
                        flat_frame[local_position]
                        & 0b11111110
                    ) | bit

        writer.write(frame)

        frames_processed += 1

    video.release()
    writer.release()

    # For randomized embedding, all payload bits
    # should have been assigned to valid frames.
    if position_key is None:

        if bit_index != required_bits:

            raise ValueError(
                "Video ended before the entire "
                "payload could be embedded."
            )

    return {
        "payload_bits": required_bits,
        "available_bits": available_bits,
        "frames_processed": frames_processed,
        "output_path": output_path,
        "encrypted": (
            password is not None
            and password != ""
        ),
        "randomized_positions": (
            position_key is not None
            and position_key != ""
        ),
    }