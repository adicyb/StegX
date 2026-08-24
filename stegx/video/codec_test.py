import os

import cv2


def check_video_codec(
    input_path: str,
    output_path: str,
    codec_name: str,
    max_frames: int = 100,
) -> dict:
    """
    Check whether OpenCV can read an input video and
    write frames using the specified codec.

    This is a utility function used by the StegX CLI.
    """

    # Open the input video.
    video = cv2.VideoCapture(input_path)

    if not video.isOpened():

        raise ValueError(
            "Could not open the input video."
        )

    # Read video properties.
    width = int(
        video.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        video.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    fps = video.get(
        cv2.CAP_PROP_FPS
    )

    # Create the codec identifier.
    fourcc = cv2.VideoWriter_fourcc(
        *codec_name
    )

    # Create the output video.
    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height),
    )

    if not writer.isOpened():

        video.release()

        raise ValueError(
            f"Could not initialize codec: "
            f"{codec_name}"
        )

    frames_written = 0

    # Copy frames into the output video.
    while frames_written < max_frames:

        success, frame = video.read()

        if not success:
            break

        writer.write(frame)

        frames_written += 1

    # Release resources.
    video.release()
    writer.release()

    # Verify that the output file was created.
    file_exists = os.path.exists(
        output_path
    )

    file_size = (
        os.path.getsize(output_path)
        if file_exists
        else 0
    )

    return {
        "codec": codec_name,
        "frames_written": frames_written,
        "output_path": output_path,
        "file_exists": file_exists,
        "file_size": file_size,
    }