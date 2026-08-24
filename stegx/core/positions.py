import hashlib
import random


def generate_positions(
    total_positions: int,
    required_positions: int,
    key: str,
) -> list[int]:
    """
    Generate deterministic randomized positions.

    The same key and total number of positions will
    always generate the same sequence of positions.
    """

    if required_positions > total_positions:

        raise ValueError(
            "Required positions cannot exceed "
            "total available positions."
        )

    if not key:

        raise ValueError(
            "A position key is required."
        )

    # Convert the user-provided key into a stable
    # integer seed using SHA-256.
    key_hash = hashlib.sha256(
        key.encode("utf-8")
    ).digest()

    seed = int.from_bytes(
        key_hash,
        byteorder="big",
    )

    # Create an isolated random generator so we do
    # not affect Python's global random state.
    generator = random.Random(seed)

    # Generate unique randomized positions.
    positions = generator.sample(
        range(total_positions),
        required_positions,
    )

    return positions