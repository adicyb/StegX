from stegx.video.analyze import get_video_info


def get_video_capacity(video_path: str) -> dict:
    """
    Calculate the theoretical LSB capacity of a video.

    StegX uses 1 least significant bit from each
    color channel: Blue, Green, and Red.
    """

    # Get information about the video.
    info = get_video_info(video_path)

    width = info["width"]
    height = info["height"]
    frame_count = info["frame_count"]

    # Each pixel has 3 usable channels:
    # Blue, Green, Red.
    bits_per_frame = (
        width
        * height
        * 3
    )

    # Total capacity across all frames.
    available_bits = (
        bits_per_frame
        * frame_count
    )

    # Convert bits to bytes.
    available_bytes = (
        available_bits // 8
    )

    return {
        **info,
        "bits_per_frame": bits_per_frame,
        "available_bits": available_bits,
        "available_bytes": available_bytes,
    }