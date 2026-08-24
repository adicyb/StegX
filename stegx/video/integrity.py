import cv2
import numpy as np


def compare_video_frames(
    original_path: str,
    test_path: str,
    max_frames: int = 100,
) -> dict:
    """
    Compare frames from two videos pixel by pixel.

    This is used to verify whether a codec preserves
    the exact pixel values required for LSB steganography.
    """

    original = cv2.VideoCapture(original_path)
    test = cv2.VideoCapture(test_path)

    if not original.isOpened():
        raise ValueError(
            "Could not open the original video."
        )

    if not test.isOpened():

        original.release()

        raise ValueError(
            "Could not open the test video."
        )

    frames_compared = 0
    total_different_pixels = 0
    maximum_difference = 0

    while frames_compared < max_frames:

        success_original, frame_original = (
            original.read()
        )

        success_test, frame_test = (
            test.read()
        )

        # Stop when either video ends.
        if (
            not success_original
            or not success_test
        ):
            break

        # Make sure frame dimensions match.
        if (
            frame_original.shape
            != frame_test.shape
        ):

            original.release()
            test.release()

            raise ValueError(
                "Video frame dimensions do not match."
            )

        # Calculate absolute pixel differences.
        difference = cv2.absdiff(
            frame_original,
            frame_test,
        )

        # Count every channel value that changed.
        different_values = np.count_nonzero(
            difference
        )

        total_different_pixels += (
            different_values
        )

        # Find the largest difference between values.
        frame_max_difference = int(
            np.max(difference)
        )

        if (
            frame_max_difference
            > maximum_difference
        ):
            maximum_difference = (
                frame_max_difference
            )

        frames_compared += 1

    original.release()
    test.release()

    identical = (
        total_different_pixels == 0
    )

    return {
        "frames_compared": frames_compared,
        "different_values": (
            total_different_pixels
        ),
        "maximum_difference": (
            maximum_difference
        ),
        "identical": identical,
    }