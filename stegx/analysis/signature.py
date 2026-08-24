from PIL import Image

from stegx.core.payload import MAGIC, get_payload_info


def extract_lsb_data(image_path: str) -> bytes:
    """
    Extract LSB data from an image and convert it
    back into raw bytes.
    """

    image = Image.open(image_path).convert("RGB")

    bits = []

    for red, green, blue in image.getdata():
        bits.append(str(red & 1))
        bits.append(str(green & 1))
        bits.append(str(blue & 1))

    bit_string = "".join(bits)

    usable_length = len(bit_string) - (len(bit_string) % 8)

    return bytes(
        int(bit_string[i:i + 8], 2)
        for i in range(0, usable_length, 8)
    )


def analyze_signature(image_path: str) -> dict:
    """
    Check whether an image contains a valid StegX signature.
    """

    raw_data = extract_lsb_data(image_path)

    # Check whether the STEGX signature exists.
    if raw_data[:len(MAGIC)] != MAGIC:
        return {
            "detected": False
        }

    try:
        info = get_payload_info(raw_data)

        expected_end = (
            info["header_size"]
            + info["payload_size"]
        )

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