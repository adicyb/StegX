from pathlib import Path

from PIL import Image

from stegx.core.crypto import decrypt_data
from stegx.core.payload import (
    MAGIC,
    get_payload_info,
)
from stegx.core.positions import generate_positions


def extract_lsb_bits(image: Image.Image) -> str:
    """
    Extract the least significant bit from every
    RGB channel in sequential order.
    """

    pixels = list(
        image.convert("RGB").getdata()
    )

    bits = []

    for red, green, blue in pixels:

        bits.append(str(red & 1))
        bits.append(str(green & 1))
        bits.append(str(blue & 1))

    return "".join(bits)


def extract_randomized_bits(
    image: Image.Image,
    required_bits: int,
    position_key: str,
) -> str:
    """
    Extract LSB bits from deterministic randomized
    positions generated using the provided key.
    """

    pixels = list(
        image.convert("RGB").getdata()
    )

    # Each RGB pixel provides three available
    # embedding positions.
    total_positions = len(pixels) * 3

    positions = generate_positions(
        total_positions=total_positions,
        required_positions=required_bits,
        key=position_key,
    )

    bits = []

    for position in positions:

        pixel_index = position // 3

        channel_index = position % 3

        pixel = pixels[pixel_index]

        channel_value = pixel[channel_index]

        bits.append(
            str(channel_value & 1)
        )

    return "".join(bits)


def bits_to_bytes(bits: str) -> bytes:
    """
    Convert a string of bits into bytes.
    """

    usable_length = (
        len(bits) - (len(bits) % 8)
    )

    return bytes(
        int(bits[i:i + 8], 2)
        for i in range(
            0,
            usable_length,
            8,
        )
    )


def extract_payload(
    image_path: str,
    output_directory: str = "samples/extracted",
    password: str | None = None,
    position_key: str | None = None,
) -> dict:
    """
    Extract a StegX payload from an image.

    Supports both sequential and randomized
    embedding positions.

    If the payload is encrypted, a password is required.
    If randomized embedding was used, the same
    position key is required.
    """

    image = Image.open(
        image_path
    ).convert("RGB")

    # ------------------------------------------
    # SEQUENTIAL EXTRACTION
    # ------------------------------------------

    if not position_key:

        bits = extract_lsb_bits(
            image
        )

        raw_data = bits_to_bytes(
            bits
        )

        # Check for StegX signature.
        if raw_data[:len(MAGIC)] != MAGIC:

            raise ValueError(
                "No valid StegX payload signature "
                "found. If this image was embedded "
                "using randomized positions, provide "
                "the correct position key."
            )

    # ------------------------------------------
    # RANDOMIZED EXTRACTION
    # ------------------------------------------

    else:

        # We first need enough bits to recover the
        # StegX header.
        #
        # Minimum structure:
        #
        # MAGIC         5 bytes
        # VERSION       1 byte
        # FLAGS         1 byte
        # FILENAME LEN  2 bytes
        #
        # = 9 bytes

        initial_bits_required = 9 * 8

        initial_bits = extract_randomized_bits(
            image=image,
            required_bits=initial_bits_required,
            position_key=position_key,
        )

        initial_data = bits_to_bytes(
            initial_bits
        )

        # Check signature.
        if initial_data[:len(MAGIC)] != MAGIC:

            raise ValueError(
                "No valid StegX payload signature "
                "found. The position key may be "
                "incorrect."
            )

        # Read filename length.
        filename_length = int.from_bytes(
            initial_data[7:9],
            byteorder="little",
        )

        # Full non-encryption-aware header:
        #
        # MAGIC         5
        # VERSION       1
        # FLAGS         1
        # FILENAME LEN  2
        # FILENAME      variable
        # PAYLOAD SIZE  8

        base_header_bytes = (
            5
            + 1
            + 1
            + 2
            + filename_length
            + 8
        )

        # Extract enough bits for the complete
        # base header.
        header_bits = extract_randomized_bits(
            image=image,
            required_bits=base_header_bytes * 8,
            position_key=position_key,
        )

        header_data = bits_to_bytes(
            header_bits
        )

        # Read encryption flag.
        flags = header_data[6]

        encrypted = bool(
            flags & 0x01
        )

        # Read payload size.
        payload_size = int.from_bytes(
            header_data[
                base_header_bytes - 8:
                base_header_bytes
            ],
            byteorder="little",
        )

        # Encrypted payloads include a
        # 16-byte salt.
        salt_size = 16 if encrypted else 0

        total_payload_bytes = (
            base_header_bytes
            + salt_size
            + payload_size
        )

        # Extract the complete payload using
        # the exact same randomized positions.
        bits = extract_randomized_bits(
            image=image,
            required_bits=(
                total_payload_bytes * 8
            ),
            position_key=position_key,
        )

        raw_data = bits_to_bytes(
            bits
        )

    # ------------------------------------------
    # PARSE PAYLOAD
    # ------------------------------------------

    info = get_payload_info(
        raw_data
    )

    header_size = info[
        "header_size"
    ]

    payload_size = info[
        "payload_size"
    ]

    # Extract stored payload data.
    payload_data = raw_data[
        header_size:
        header_size + payload_size
    ]

    if len(payload_data) != payload_size:

        raise ValueError(
            "Payload appears to be incomplete "
            "or corrupted."
        )

    # ------------------------------------------
    # DECRYPT IF NECESSARY
    # ------------------------------------------

    if info["encrypted"]:

        if not password:

            raise ValueError(
                "This payload is encrypted. "
                "A password is required."
            )

        payload_data = decrypt_data(
            payload_data,
            password,
            info["salt"],
        )

    # ------------------------------------------
    # SAVE RECOVERED FILE
    # ------------------------------------------

    output_path = Path(
        output_directory
    )

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    recovered_file = (
        output_path
        / info["filename"]
    )

    with open(
        recovered_file,
        "wb",
    ) as file:

        file.write(
            payload_data
        )

    return {
        "filename": info["filename"],
        "payload_size": len(
            payload_data
        ),
        "encrypted": info[
            "encrypted"
        ],
        "randomized_positions": (
            position_key is not None
            and position_key != ""
        ),
        "output_path": str(
            recovered_file
        ),
    }


def get_displayable_content(
    file_path: str,
):
    """
    Return file content if it is a readable text file.
    Return None for binary files.
    """

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:

            return file.read()

    except (
        UnicodeDecodeError,
        OSError,
    ):

        return None