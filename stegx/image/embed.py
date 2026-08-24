from pathlib import Path

from PIL import Image

from stegx.core.payload import create_payload
from stegx.core.positions import generate_positions


SAFE_FORMATS = {
    ".png",
    ".bmp",
    ".tiff",
    ".tif",
}

LOSSY_FORMATS = {
    ".jpg",
    ".jpeg",
    ".webp",
}


def bytes_to_bits(data: bytes) -> str:
    """
    Convert bytes into a string of binary bits.
    """

    return "".join(
        format(byte, "08b")
        for byte in data
    )


def get_safe_output_path(
    input_path: str,
    output_path: str,
) -> tuple[str, bool]:
    """
    Determine whether the requested output format
    is safe for LSB steganography.

    Returns:
        final_output_path,
        format_changed
    """

    output_suffix = Path(
        output_path
    ).suffix.lower()

    # If output has no extension, use PNG.
    if not output_suffix:

        output_path = f"{output_path}.png"
        output_suffix = ".png"

    # Lossy formats can destroy LSB data.
    if output_suffix in LOSSY_FORMATS:

        output_path = str(
            Path(output_path).with_suffix(
                ".png"
            )
        )

        return output_path, True

    # Unknown formats are converted to PNG.
    if output_suffix not in SAFE_FORMATS:

        output_path = str(
            Path(output_path).with_suffix(
                ".png"
            )
        )

        return output_path, True

    return output_path, False


def embed_payload(
    image_path: str,
    payload_path: str,
    output_path: str,
    password: str | None = None,
    position_key: str | None = None,
):
    """
    Embed a StegX payload inside an image using
    1-bit LSB embedding across RGB channels.

    If a position key is provided, payload bits are
    embedded at deterministic randomized positions.

    Unsafe output formats are automatically converted
    to PNG to preserve the embedded payload.
    """

    # Determine safe output format.
    final_output_path, format_changed = (
        get_safe_output_path(
            image_path,
            output_path,
        )
    )

    # Load carrier image.
    image = Image.open(
        image_path
    ).convert("RGB")

    # Create structured StegX payload.
    payload = create_payload(
        payload_path,
        password=password,
    )

    # Convert payload into bits.
    payload_bits = bytes_to_bits(
        payload
    )

    required_bits = len(
        payload_bits
    )

    width, height = image.size

    # RGB provides three channels per pixel.
    available_bits = (
        width
        * height
        * 3
    )

    if required_bits > available_bits:

        raise ValueError(
            "Payload is too large for this image. "
            f"Required: {required_bits} bits, "
            f"Available: {available_bits} bits."
        )

    # Get all pixels.
    pixels = list(
        image.get_flattened_data()
    )

    # Convert pixels into a flat list:
    #
    # [R, G, B, R, G, B, ...]
    channels = []

    for red, green, blue in pixels:

        channels.extend(
            [red, green, blue]
        )

    # ---------------------------------------------
    # POSITION SELECTION
    # ---------------------------------------------

    if position_key:

        positions = generate_positions(
            total_positions=available_bits,
            required_positions=required_bits,
            key=position_key,
        )

        randomized = True

    else:

        # Default sequential embedding.
        positions = list(
            range(required_bits)
        )

        randomized = False

    # ---------------------------------------------
    # EMBED PAYLOAD BITS
    # ---------------------------------------------

    for bit_index, position in enumerate(
        positions
    ):

        bit = int(
            payload_bits[bit_index]
        )

        channels[position] = (
            channels[position]
            & 0b11111110
        ) | bit

    # ---------------------------------------------
    # REBUILD PIXELS
    # ---------------------------------------------

    modified_pixels = []

    for index in range(
        0,
        len(channels),
        3,
    ):

        modified_pixels.append(
            (
                channels[index],
                channels[index + 1],
                channels[index + 2],
            )
        )

    # Create modified image.
    stego_image = Image.new(
        "RGB",
        image.size,
    )

    stego_image.putdata(
        modified_pixels
    )

    # Save output.
    stego_image.save(
        final_output_path
    )

    return {
        "payload_bits": required_bits,
        "available_bits": available_bits,
        "pixels_modified": (
            required_bits + 2
        ) // 3,
        "output_path": final_output_path,
        "encrypted": (
            password is not None
            and password != ""
        ),
        "randomized_positions": randomized,
        "format_changed": format_changed,
    }