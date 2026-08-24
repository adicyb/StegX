from pathlib import Path

import cv2
import numpy as np

from stegx.video.embed import embed_video_payload
from stegx.video.extract import extract_video_payload


def create_test_video(
    video_path: Path,
    width: int = 64,
    height: int = 64,
    frames: int = 10,
):
    """
    Create a small lossless test video.
    """

    fourcc = cv2.VideoWriter_fourcc(
        *"FFV1"
    )

    writer = cv2.VideoWriter(
        str(video_path),
        fourcc,
        10.0,
        (width, height),
    )

    if not writer.isOpened():
        raise RuntimeError(
            "Could not create test video."
        )

    for _ in range(frames):

        frame = np.random.randint(
            0,
            256,
            (height, width, 3),
            dtype=np.uint8,
        )

        writer.write(frame)

    writer.release()


def test_video_embed_and_extract(tmp_path):

    video_path = tmp_path / "carrier.avi"
    secret_path = tmp_path / "secret.txt"
    output_video = tmp_path / "stego.avi"
    output_directory = tmp_path / "extracted"

    create_test_video(video_path)

    secret_content = "Hello from StegX video"

    secret_path.write_text(
        secret_content
    )

    embed_video_payload(
        video_path=str(video_path),
        payload_path=str(secret_path),
        output_path=str(output_video),
    )

    result = extract_video_payload(
        video_path=str(output_video),
        output_directory=str(output_directory),
    )

    recovered_path = Path(
        result["output_path"]
    )

    assert recovered_path.exists()

    assert recovered_path.read_text() == (
        secret_content
    )

    assert result["encrypted"] is False


def test_randomized_video_embed_and_extract(
    tmp_path,
):

    video_path = tmp_path / "carrier.avi"
    secret_path = tmp_path / "secret.txt"
    output_video = tmp_path / "random_stego.avi"
    output_directory = tmp_path / "extracted"

    position_key = "mysecretkey"

    create_test_video(video_path)

    secret_content = "Randomized StegX video"

    secret_path.write_text(
        secret_content
    )

    embed_video_payload(
        video_path=str(video_path),
        payload_path=str(secret_path),
        output_path=str(output_video),
        position_key=position_key,
    )

    result = extract_video_payload(
        video_path=str(output_video),
        output_directory=str(output_directory),
        position_key=position_key,
    )

    recovered_path = Path(
        result["output_path"]
    )

    assert recovered_path.exists()

    assert recovered_path.read_text() == (
        secret_content
    )

    assert result["encrypted"] is False


def test_encrypted_randomized_video_workflow(
    tmp_path,
):

    video_path = tmp_path / "carrier.avi"
    secret_path = tmp_path / "secret.txt"
    output_video = tmp_path / "encrypted_stego.avi"
    output_directory = tmp_path / "extracted"

    password = "mypassword123"
    position_key = "mysecretkey"

    create_test_video(video_path)

    secret_content = (
        "Encrypted randomized StegX video"
    )

    secret_path.write_text(
        secret_content
    )

    embed_video_payload(
        video_path=str(video_path),
        payload_path=str(secret_path),
        output_path=str(output_video),
        password=password,
        position_key=position_key,
    )

    result = extract_video_payload(
        video_path=str(output_video),
        output_directory=str(output_directory),
        password=password,
        position_key=position_key,
    )

    recovered_path = Path(
        result["output_path"]
    )

    assert recovered_path.exists()

    assert recovered_path.read_text() == (
        secret_content
    )

    assert result["encrypted"] is True