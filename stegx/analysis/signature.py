from PIL import Image

from stegx.core.payload import (
    MAGIC,
    get_payload_info,
)

from stegx.core.positions import (
    generate_positions,
)


def bits_to_bytes(bits: list[int]) -> bytes:
    """
    Convert a list of bits into raw bytes.
    """

    usable_length = (
        len(bits) - (len(bits) % 8)
    )

    output = bytearray()

    for index in range(
        0,
        usable_length,
        8,
    ):

        value = 0

        for bit in bits[
            index:index + 8
        ]:

            value = (
                value << 1
            ) | bit

        output.append(value)

    return bytes(output)


def extract_lsb_data(
    image_path: str,
    position_key: str | None = None,
) -> bytes:
    """
    Extract LSB data from an image.

    If position_key is provided, reproduce the
    randomized embedding positions.
    Otherwise, extract sequentially from all RGB
    channels.
    """

    image = Image.open(
        image_path
    ).convert("RGB")

    pixels = list(
        image.getdata()
    )

    # --------------------------------------------
    # NORMAL SEQUENTIAL EXTRACTION
    # --------------------------------------------

    if not position_key:

        bits = []

        for red, green, blue in pixels:

            bits.append(red & 1)
            bits.append(green & 1)
            bits.append(blue & 1)

        return bits_to_bytes(bits)

    # --------------------------------------------
    # RANDOMIZED POSITION EXTRACTION
    # --------------------------------------------

    total_positions = (
        len(pixels) * 3
    )

    # We initially only need enough bits to recover
    # the payload header.
    #
    # MAGIC        5 bytes
    # VERSION      1 byte
    # FLAGS        1 byte
    # FILENAME LEN 2 bytes
    #
    # Total = 9 bytes = 72 bits
    initial_bits_required = 72

    initial_positions = generate_positions(
        total_positions,
        initial_bits_required,
        position_key,
    )

    flat_channels = []

    for red, green, blue in pixels:

        flat_channels.extend(
            [red, green, blue]
        )

    bits = []

    for position in initial_positions:

        bits.append(
            flat_channels[position] & 1
        )

    initial_data = bits_to_bytes(bits)

    # Verify the STEGX signature before continuing.
    if (
        initial_data[:len(MAGIC)]
        != MAGIC
    ):

        return initial_data

    # --------------------------------------------
    # READ FILENAME LENGTH
    # --------------------------------------------

    filename_length = int.from_bytes(
        initial_data[7:9],
        byteorder="little",
    )

    # Complete header:
    #
    # MAGIC          5 bytes
    # VERSION        1 byte
    # FLAGS          1 byte
    # FILENAME LEN   2 bytes
    # FILENAME       variable
    # PAYLOAD SIZE   8 bytes

    header_size = (
        5
        + 1
        + 1
        + 2
        + filename_length
        + 8
    )

    # To read the complete header.
    header_bits_required = (
        header_size * 8
    )

    header_positions = generate_positions(
        total_positions,
        header_bits_required,
        position_key,
    )

    bits = []

    for position in header_positions:

        bits.append(
            flat_channels[position] & 1
        )

    header_data = bits_to_bytes(bits)

    # --------------------------------------------
    # PARSE HEADER
    # --------------------------------------------

    try:

        info = get_payload_info(
            header_data
        )

    except Exception:

        return header_data

    # Calculate total stored payload size.
    #
    # For encrypted payloads, the salt is stored
    # separately and must also be recovered.

    total_payload_bytes = (
        info["header_size"]
        + info["payload_size"]
    )

    if info["encrypted"]:

        total_payload_bytes += 16

    total_bits_required = (
        total_payload_bytes * 8
    )

    if (
        total_bits_required
        > total_positions
    ):

        raise ValueError(
            "The image does not contain enough "
            "positions for the expected payload."
        )

    # --------------------------------------------
    # REGENERATE ALL RANDOMIZED POSITIONS
    # --------------------------------------------

    all_positions = generate_positions(
        total_positions,
        total_bits_required,
        position_key,
    )

    bits = []

    for position in all_positions:

        bits.append(
            flat_channels[position] & 1
        )

    return bits_to_bytes(bits)


def analyze_signature(
    image_path: str,
    position_key: str | None = None,
) -> dict:
    """
    Check whether an image contains a valid
    StegX payload signature.

    Supports both sequential and keyed
    randomized embedding.
    """

    raw_data = extract_lsb_data(
        image_path,
        position_key=position_key,
    )

    # Check for STEGX magic.
    if (
        raw_data[:len(MAGIC)]
        != MAGIC
    ):

        return {
            "detected": False
        }

    try:

        info = get_payload_info(
            raw_data
        )

        expected_end = (
            info["header_size"]
            + info["payload_size"]
        )

        # Encrypted payloads also include
        # a 16-byte salt.

        if info["encrypted"]:

            expected_end += 16

        # Make sure the complete payload exists.

        if expected_end > len(raw_data):

            return {
                "detected": False
            }

        return {
            "detected": True,
            **info,
        }

    except Exception:

        return {
            "detected": False
        }