import math

from PIL import Image


def get_lsb_statistics(image_path: str) -> dict:
    """
    Analyze the least significant bits of an image.
    """

    image = Image.open(image_path).convert("RGB")

    zero_count = 0
    one_count = 0

    total_bits = 0

    for red, green, blue in image.getdata():

        channels = [red, green, blue]

        for value in channels:

            lsb = value & 1

            if lsb == 0:
                zero_count += 1
            else:
                one_count += 1

            total_bits += 1

    return {
        "total_bits": total_bits,
        "zero_count": zero_count,
        "one_count": one_count,
    }


def calculate_entropy(zero_count: int, one_count: int) -> float:
    """
    Calculate Shannon entropy for the binary LSB distribution.
    """

    total = zero_count + one_count

    if total == 0:
        return 0.0

    probability_zero = zero_count / total
    probability_one = one_count / total

    entropy = 0.0

    if probability_zero > 0:
        entropy -= probability_zero * math.log2(
            probability_zero
        )

    if probability_one > 0:
        entropy -= probability_one * math.log2(
            probability_one
        )

    return entropy


def calculate_chi_square(
    zero_count: int,
    one_count: int,
) -> float:
    """
    Calculate a simple chi-square statistic by comparing
    the observed LSB distribution with an expected 50/50 split.
    """

    total = zero_count + one_count

    if total == 0:
        return 0.0

    expected = total / 2

    chi_square = (
        ((zero_count - expected) ** 2) / expected
        +
        ((one_count - expected) ** 2) / expected
    )

    return chi_square


def analyze_heuristics(image_path: str) -> dict:
    """
    Perform basic heuristic analysis for possible
    LSB steganographic characteristics.
    """

    stats = get_lsb_statistics(image_path)

    total_bits = stats["total_bits"]
    zero_count = stats["zero_count"]
    one_count = stats["one_count"]

    entropy = calculate_entropy(
        zero_count,
        one_count,
    )

    chi_square = calculate_chi_square(
        zero_count,
        one_count,
    )

    zero_ratio = (zero_count / total_bits) * 100
    one_ratio = (one_count / total_bits) * 100

    # Calculate how close the distribution is to 50/50.
    balance_difference = abs(
        zero_ratio - one_ratio
    )

    # Simple suspicion scoring.
    suspicion_score = 0

    # A highly balanced LSB distribution may indicate
    # randomized or embedded data.
    if balance_difference < 1:
        suspicion_score += 35

    elif balance_difference < 3:
        suspicion_score += 20

    # Maximum binary entropy is 1.0.
    if entropy > 0.99:
        suspicion_score += 35

    elif entropy > 0.95:
        suspicion_score += 20

    # Very low chi-square means the observed values
    # are close to an even 50/50 distribution.
    if chi_square < 1:
        suspicion_score += 30

    elif chi_square < 5:
        suspicion_score += 15

    suspicion_score = min(
        suspicion_score,
        100,
    )

    if suspicion_score >= 70:
        verdict = "High suspicion"

    elif suspicion_score >= 40:
        verdict = "Possible suspicion"

    else:
        verdict = "Low suspicion"

    return {
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