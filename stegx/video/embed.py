import cv2
import numpy as np

from stegx.core.payload import create_payload


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
):
    """
    Embed a StegX payload into a video using
    1-bit LSB steganography across BGR channels.

    The output video uses the FFV1 lossless codec
    to preserve the embedded LSB data.
    """

    # Open the input video.
    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise ValueError(
            "Could not open the input video."
        )

    # Read video metadata.
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

    # 3 channels: Blue, Green, Red.
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

    # FFV1 is our tested lossless codec.
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

    while True:

        success, frame = video.read()

        if not success:
            break

        # Only modify frames while there are
        # payload bits remaining.
        if bit_index < required_bits:

            # Flatten frame:
            # (height, width, 3)
            # becomes one continuous array.
            flat_frame = frame.reshape(-1)

            remaining_bits = (
                required_bits - bit_index
            )

            usable_values = min(
                remaining_bits,
                len(flat_frame),
            )

            # Convert the next payload bits
            # into a NumPy array.
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

            # Clear the LSB of each channel value.
            flat_frame[:usable_values] &= 0b11111110

            # Insert the payload bits.
            flat_frame[:usable_values] |= bits

            bit_index += usable_values

        # Write the frame to the FFV1 output.
        writer.write(frame)

        frames_processed += 1

    video.release()
    writer.release()

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
    }