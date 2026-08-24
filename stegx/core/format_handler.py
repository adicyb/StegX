from pathlib import Path


SAFE_IMAGE_FORMATS = {
    ".png": {
        "name": "PNG",
        "lossy": False,
        "safe_for_lsb": True,
        "recommended_output": ".png",
    },
    ".bmp": {
        "name": "BMP",
        "lossy": False,
        "safe_for_lsb": True,
        "recommended_output": ".bmp",
    },
    ".tiff": {
        "name": "TIFF",
        "lossy": False,
        "safe_for_lsb": True,
        "recommended_output": ".tiff",
    },
    ".tif": {
        "name": "TIFF",
        "lossy": False,
        "safe_for_lsb": True,
        "recommended_output": ".tiff",
    },
}


CONDITIONAL_IMAGE_FORMATS = {
    ".jpg": {
        "name": "JPEG",
        "lossy": True,
        "safe_for_lsb": False,
        "recommended_output": ".png",
    },
    ".jpeg": {
        "name": "JPEG",
        "lossy": True,
        "safe_for_lsb": False,
        "recommended_output": ".png",
    },
    ".webp": {
        "name": "WEBP",
        "lossy": True,
        "safe_for_lsb": False,
        "recommended_output": ".png",
    },
}


VIDEO_FORMATS = {
    ".mp4": {
        "name": "MP4",
        "type": "video",
    },
    ".mkv": {
        "name": "MKV",
        "type": "video",
    },
    ".avi": {
        "name": "AVI",
        "type": "video",
    },
    ".mov": {
        "name": "MOV",
        "type": "video",
    },
}


def get_file_extension(file_path: str) -> str:
    """
    Return the file extension in lowercase.
    """

    return Path(file_path).suffix.lower()


def get_media_info(file_path: str) -> dict:
    """
    Detect the media type and return information
    about the file format.
    """

    extension = get_file_extension(file_path)

    if extension in SAFE_IMAGE_FORMATS:
        info = SAFE_IMAGE_FORMATS[extension].copy()

        return {
            "extension": extension,
            "media_type": "image",
            "supported": True,
            **info,
        }

    if extension in CONDITIONAL_IMAGE_FORMATS:
        info = CONDITIONAL_IMAGE_FORMATS[extension].copy()

        return {
            "extension": extension,
            "media_type": "image",
            "supported": True,
            **info,
        }

    if extension in VIDEO_FORMATS:
        info = VIDEO_FORMATS[extension].copy()

        return {
            "extension": extension,
            "media_type": "video",
            "supported": True,
            "lossy": None,
            "safe_for_lsb": None,
            "recommended_output": None,
            **info,
        }

    return {
        "extension": extension,
        "media_type": "unknown",
        "supported": False,
        "name": "Unknown",
        "lossy": None,
        "safe_for_lsb": False,
        "recommended_output": None,
    }


def print_media_info(file_path: str):
    """
    Print detected media information.
    """

    info = get_media_info(file_path)

    print("\n--- Media Analysis ---")

    print(f"File: {file_path}")
    print(f"Extension: {info['extension']}")
    print(f"Media Type: {info['media_type']}")
    print(f"Format: {info['name']}")
    print(f"Supported: {info['supported']}")

    if info["media_type"] == "image":
        print(f"Lossy: {info['lossy']}")
        print(f"Safe for LSB: {info['safe_for_lsb']}")

        if not info["safe_for_lsb"]:
            print(
                f"Warning: Direct LSB embedding is not recommended. "
                f"Suggested output: {info['recommended_output']}"
            )