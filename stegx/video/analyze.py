from pathlib import Path

import cv2


SUPPORTED_VIDEO_FORMATS = {
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".webm",
}


def get_video_info(video_path: str) -> dict:
    """
    Read basic metadata from a video file.
    """

    path = Path(video_path)

    # Check whether the file exists.
    if not path.exists():
        raise FileNotFoundError(video_path)

    # Get the extension, for example .mp4.
    extension = path.suffix.lower()

    # Check whether StegX currently supports it.
    if extension not in SUPPORTED_VIDEO_FORMATS:
        raise ValueError(
            f"Unsupported video format: {extension}"
        )

    # Open the video using OpenCV.
    video = cv2.VideoCapture(str(video_path))

    if not video.isOpened():
        raise ValueError(
            "Could not open the video file."
        )

    # Read video resolution.
    width = int(
        video.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    # Read frames per second.
    fps = video.get(
        cv2.CAP_PROP_FPS
    )

    # Read total number of frames.
    frame_count = int(
        video.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    # Calculate duration.
    duration = (
        frame_count / fps
        if fps > 0
        else 0
    )

    # Read codec information.
    fourcc = int(
        video.get(
            cv2.CAP_PROP_FOURCC
        )
    )

    codec = "".join(
        chr((fourcc >> (8 * i)) & 0xFF)
        for i in range(4)
    )

    # Always release the video after reading it.
    video.release()

    return {
        "path": str(path),
        "extension": extension,
        "width": width,
        "height": height,
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration,
        "codec": codec,
    }