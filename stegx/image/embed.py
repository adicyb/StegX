from pathlib import Path

from PIL import Image

from stegx.core.payload import create_payload


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

    input_suffix = Path(input_path).suffix.lower()
    output_suffix = Path(output_path).suffix.lower()

    # If output has no extension, use PNG.
    if not output_suffix:
        output_path = f"{output_path}.png"
        output_suffix = ".png"

    # Lossy output formats are unsafe because
    # compression can destroy embedded LSB data.
    if output_suffix in LOSSY_FORMATS:

        output_path = str(
            Path(output_path).with_suffix(".png")
        )

        return output_path, True

    # Unknown formats are also converted to PNG.
    if output_suffix not in SAFE_FORMATS:

        output_path = str(
            Path(output_path).with_suffix(".png")
        )

        return output_path, True

    return output_path, False


def embed_payload(
    image_path: str,
    payload_path: str,
    output_path: str,
    password: str | None = None,
):
    """
    Embed a StegX payload inside an image using
    1-bit LSB embedding across RGB channels.

    Unsafe output formats are automatically converted
    to PNG to preserve the embedded payload.
    """

    # Determine a safe output format.
    final_output_path, format_changed = (
        get_safe_output_path(
            image_path,
            output_path,
        )
    )

    # Load the carrier image.
    image = Image.open(image_path).convert("RGB")

    # Create the structured StegX payload.
    payload = create_payload(
        payload_path,
        password=password,
    )

    # Convert payload bytes into bits.
    payload_bits = bytes_to_bits(payload)

    required_bits = len(payload_bits)

    width, height = image.size

    # RGB provides three usable channels per pixel.
    available_bits = width * height * 3

    if required_bits > available_bits:
        raise ValueError(
            "Payload is too large for this image. "
            f"Required: {required_bits} bits, "
            f"Available: {available_bits} bits."
        )

    pixels = list(image.getdata())

    modified_pixels = []

    bit_index = 0

    for red, green, blue in pixels:

        channels = [red, green, blue]

        for channel_index in range(3):

            if bit_index < required_bits:

                bit = int(
                    payload_bits[bit_index]
                )

                channels[channel_index] = (
                    channels[channel_index]
                    & 0b11111110
                ) | bit

                bit_index += 1

        modified_pixels.append(
            tuple(channels)
        )

    # Create the modified image.
    stego_image = Image.new(
        "RGB",
        image.size,
    )

    stego_image.putdata(
        modified_pixels
    )

    # Save using the safe format.
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
        "format_changed": format_changed,
    }