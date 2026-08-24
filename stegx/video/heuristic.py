import math

import cv2
import numpy as np


def calculate_entropy(
    zero_count: int,
    one_count: int,
) -> float:
    """
    Calculate Shannon entropy for the
    binary LSB distribution.
    """

    total = zero_count + one_count

    if total == 0:
        return 0.0

    zero_probability = zero_count / total
    one_probability = one_count / total

    entropy = 0.0

    if zero_probability > 0:
        entropy -= (
            zero_probability
            * math.log2(zero_probability)
        )

    if one_probability > 0:
        entropy -= (
            one_probability
            * math.log2(one_probability)
        )

    return entropy


def analyze_video_heuristics(
    video_path: str,
    sample_frames: int = 20,
) -> dict:
    """
    Analyze sampled video frames for possible
    LSB steganographic characteristics.
    """

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():

        raise ValueError(
            "Could not open the video."
        )

    total_frames = int(
        video.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if total_frames <= 0:

        video.release()

        raise ValueError(
            "Could not determine video frame count."
        )

    # Decide which frames to sample.
    #
    # Example:
    # 900 frames, 20 samples
    #
    # 0, 47, 94, 142 ...
    #

    frame_indices = np.linspace(
        0,
        total_frames - 1,
        min(sample_frames, total_frames),
        dtype=int,
    )

    zero_count = 0
    one_count = 0

    frames_analyzed = 0

    for frame_index in frame_indices:

        video.set(
            cv2.CAP_PROP_POS_FRAMES,
            int(frame_index),
        )

        success, frame = video.read()

        if not success:
            continue

        # Flatten all BGR channel values.
        flat_frame = frame.reshape(-1)

        # Extract least significant bits.
        lsb_values = flat_frame & 1

        zero_count += int(
            np.sum(lsb_values == 0)
        )

        one_count += int(
            np.sum(lsb_values == 1)
        )

        frames_analyzed += 1

    video.release()

    total_bits = (
        zero_count + one_count
    )

    if total_bits == 0:

        raise ValueError(
            "No pixel data could be analyzed."
        )

    zero_ratio = (
        zero_count / total_bits
    ) * 100

    one_ratio = (
        one_count / total_bits
    ) * 100

    entropy = calculate_entropy(
        zero_count,
        one_count,
    )

    # Chi-square against an ideal
    # 50/50 distribution.

    expected = total_bits / 2

    chi_square = (
        ((zero_count - expected) ** 2)
        / expected
    )

    chi_square += (
        ((one_count - expected) ** 2)
        / expected
    )

    balance_difference = abs(
        zero_ratio - one_ratio
    )

    # ----------------------------------------
    # Suspicion scoring
    # ----------------------------------------

    suspicion_score = 0

    # Near-perfect entropy can indicate
    # artificially randomized LSB values.

    if entropy > 0.999:
        suspicion_score += 35

    elif entropy > 0.995:
        suspicion_score += 25

    elif entropy > 0.990:
        suspicion_score += 15

    # Very balanced distribution.

    if balance_difference < 1:
        suspicion_score += 35

    elif balance_difference < 3:
        suspicion_score += 20

    elif balance_difference < 5:
        suspicion_score += 10

    # Lower chi-square means closer to
    # an even 50/50 distribution.

    if chi_square < 10:
        suspicion_score += 30

    elif chi_square < 100:
        suspicion_score += 20

    elif chi_square < 1000:
        suspicion_score += 10

    suspicion_score = min(
        suspicion_score,
        100,
    )

    # ----------------------------------------
    # Verdict
    # ----------------------------------------

    if suspicion_score >= 70:

        verdict = (
            "High suspicion"
        )

    elif suspicion_score >= 40:

        verdict = (
            "Possible suspicion"
        )

    else:

        verdict = (
            "Low suspicion"
        )

    return {
        "frames_analyzed": frames_analyzed,
        "total_bits": total_bits,
        "zero_count": zero_count,
        "one_count": one_count,
        "zero_ratio": zero_ratio,
        "one_ratio": one_ratio,
        "entropy": entropy,
        "chi_square": chi_square,
        "balance_difference": balance_difference,
        "suspicion_score": suspicion_score,
        "verdict": verdict,
    }