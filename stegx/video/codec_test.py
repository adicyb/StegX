import os

import cv2


def test_video_codec(
    input_path: str,
    output_path: str,
    codec_name: str,
    max_frames: int = 100,
):
    """
    Test whether OpenCV can read a video and write
    frames using the specified codec.
    """

    video = cv2.VideoCapture(input_path)

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

    fourcc = cv2.VideoWriter_fourcc(
        *codec_name
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
            f"Could not initialize codec: "
            f"{codec_name}"
        )

    frames_written = 0

    while frames_written < max_frames:

        success, frame = video.read()

        if not success:
            break

        writer.write(frame)

        frames_written += 1

    video.release()
    writer.release()

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