from PIL import Image


def get_image_capacity(image_path: str) -> dict:
    """
    Calculate the approximate payload capacity of an image
    using 1-bit LSB embedding in RGB channels.
    """

    with Image.open(image_path) as image:

        # Convert to RGB so we consistently work with
        # Red, Green, and Blue channels.
        image = image.convert("RGB")

        width, height = image.size

        total_pixels = width * height

        # 1 bit from each RGB channel.
        available_bits = total_pixels * 3

        # Convert bits to bytes.
        available_bytes = available_bits // 8

        return {
            "width": width,
            "height": height,
            "total_pixels": total_pixels,
            "available_bits": available_bits,
            "available_bytes": available_bytes,
        }


def format_size(size_in_bytes: int) -> str:
    """
    Convert bytes into a human-readable size.
    """

    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"

    if size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"

    return f"{size_in_bytes / (1024 * 1024):.2f} MB"