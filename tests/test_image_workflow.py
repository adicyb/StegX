from pathlib import Path

from PIL import Image

from stegx.image.embed import embed_payload
from stegx.image.extract import extract_payload


def create_test_image(
    path: Path,
    width: int = 100,
    height: int = 100,
):
    """
    Create a simple RGB carrier image.
    """

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    image.save(path)


def create_test_payload(
    path: Path,
    content: bytes,
):
    """
    Create a payload file.
    """

    path.write_bytes(content)


def test_image_embed_and_extract(
    tmp_path,
):

    carrier_path = (
        tmp_path / "carrier.png"
    )

    payload_path = (
        tmp_path / "secret.txt"
    )

    stego_path = (
        tmp_path / "stego.png"
    )

    output_directory = (
        tmp_path / "extracted"
    )

    original_content = (
        b"Hello from StegX image test"
    )

    create_test_image(
        carrier_path
    )

    create_test_payload(
        payload_path,
        original_content,
    )

    # Embed the payload.
    embed_payload(
        str(carrier_path),
        str(payload_path),
        str(stego_path),
    )

    # Extract the payload.
    result = extract_payload(
        str(stego_path),
        str(output_directory),
    )

    recovered_path = Path(
        result["output_path"]
    )

    assert recovered_path.exists()

    assert recovered_path.read_bytes() == (
        original_content
    )


def test_randomized_image_embed_and_extract(
    tmp_path,
):

    carrier_path = (
        tmp_path / "carrier.png"
    )

    payload_path = (
        tmp_path / "secret.txt"
    )

    stego_path = (
        tmp_path / "random_stego.png"
    )

    output_directory = (
        tmp_path / "extracted"
    )

    original_content = (
        b"Randomized StegX image test"
    )

    position_key = "mysecretkey"

    create_test_image(
        carrier_path
    )

    create_test_payload(
        payload_path,
        original_content,
    )

    # Embed using randomized positions.
    embed_payload(
        str(carrier_path),
        str(payload_path),
        str(stego_path),
        position_key=position_key,
    )

    # Extract using the same position key.
    result = extract_payload(
        str(stego_path),
        str(output_directory),
        position_key=position_key,
    )

    recovered_path = Path(
        result["output_path"]
    )

    assert recovered_path.exists()

    assert recovered_path.read_bytes() == (
        original_content
    )


def test_encrypted_randomized_image_workflow(
    tmp_path,
):

    carrier_path = (
        tmp_path / "carrier.png"
    )

    payload_path = (
        tmp_path / "secret.txt"
    )

    stego_path = (
        tmp_path / "encrypted_stego.png"
    )

    output_directory = (
        tmp_path / "extracted"
    )

    original_content = (
        b"Encrypted randomized StegX image test"
    )

    password = "mypassword123"

    position_key = "mysecretkey"

    create_test_image(
        carrier_path
    )

    create_test_payload(
        payload_path,
        original_content,
    )

    # Embed with both encryption and
    # randomized positions.
    embed_payload(
        str(carrier_path),
        str(payload_path),
        str(stego_path),
        password=password,
        position_key=position_key,
    )

    # Extract using the correct password
    # and position key.
    result = extract_payload(
        str(stego_path),
        str(output_directory),
        password=password,
        position_key=position_key,
    )

    recovered_path = Path(
        result["output_path"]
    )

    assert recovered_path.exists()

    assert recovered_path.read_bytes() == (
        original_content
    )