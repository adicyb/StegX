from pathlib import Path

from PIL import Image

from stegx.core.crypto import decrypt_data
from stegx.core.payload import (
    MAGIC,
    get_payload_info,
)


def extract_lsb_bits(image: Image.Image) -> str:
    """
    Extract the least significant bit from every
    RGB channel in the image.
    """

    pixels = list(image.convert("RGB").getdata())

    bits = []

    for red, green, blue in pixels:
        bits.append(str(red & 1))
        bits.append(str(green & 1))
        bits.append(str(blue & 1))

    return "".join(bits)


def bits_to_bytes(bits: str) -> bytes:
    """
    Convert a string of bits into bytes.
    """

    usable_length = len(bits) - (len(bits) % 8)

    return bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, usable_length, 8)
    )


def extract_payload(
    image_path: str,
    output_directory: str = "samples/extracted",
    password: str | None = None,
) -> dict:
    """
    Extract a StegX payload from an image.

    If the payload is encrypted, a password is required.
    """

    image = Image.open(image_path).convert("RGB")

    # Extract all LSB bits.
    bits = extract_lsb_bits(image)

    # Convert bits back into bytes.
    raw_data = bits_to_bytes(bits)

    # Check for StegX signature.
    if raw_data[:len(MAGIC)] != MAGIC:
        raise ValueError(
            "No valid StegX payload signature found."
        )

    # Read metadata.
    info = get_payload_info(raw_data)

    header_size = info["header_size"]
    payload_size = info["payload_size"]

    # Extract the stored payload data.
    payload_data = raw_data[
        header_size:header_size + payload_size
    ]

    if len(payload_data) != payload_size:
        raise ValueError(
            "Payload appears to be incomplete or corrupted."
        )

    # Decrypt if necessary.
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

    # Create output directory.
    output_path = Path(output_directory)

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Restore original filename.
    recovered_file = (
        output_path / info["filename"]
    )

    with open(recovered_file, "wb") as file:
        file.write(payload_data)

    return {
        "filename": info["filename"],
        "payload_size": len(payload_data),
        "encrypted": info["encrypted"],
        "output_path": str(recovered_file),
    }


def get_displayable_content(file_path: str):
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

    except (UnicodeDecodeError, OSError):
        return None