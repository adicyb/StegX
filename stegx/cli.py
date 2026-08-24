import typer
import os

from stegx.utils.banner import show_banner
from stegx.core.format_handler import (
    print_media_info,
    get_media_info,
)
from stegx.image.capacity import get_image_capacity, format_size
from stegx.core.payload import create_payload, get_payload_info
from stegx.image.embed import embed_payload
from stegx.image.extract import (
    extract_payload,
    get_displayable_content,
)
from stegx.analysis.signature import (
    analyze_signature as run_signature_analysis,
)
from stegx.analysis.heuristic import analyze_heuristics
from stegx.video.analyze import get_video_info
from stegx.video.capacity import get_video_capacity
from stegx.video.codec_test import test_video_codec
from stegx.video.integrity import compare_video_frames
from stegx.video.embed import embed_video_payload
from stegx.video.extract import extract_video_payload
from stegx.video.detection import (
    analyze_video_signature as run_video_signature_analysis,
)
from stegx.video.heuristic import (
    analyze_video_heuristics,
)

app = typer.Typer(
    name="stegx",
    help="A CLI-based secure media steganography toolkit.",
    add_completion=False,
)


@app.callback()
def main():
    """
    StegX - Secure Media Steganography Toolkit
    """
    pass


@app.command()
def info():
    """Display information about StegX."""
    show_banner()


@app.command()
def formats():
    """Display supported media formats."""
    show_banner()

    typer.echo("Supported Image Formats:")
    typer.echo("  PNG")
    typer.echo("  BMP")
    typer.echo("  TIFF")
    typer.echo("  TIF")

    typer.echo("\nConditional Input Formats:")
    typer.echo("  JPG")
    typer.echo("  JPEG")
    typer.echo("  WEBP")

    typer.echo("\nPlanned Video Input Formats:")
    typer.echo("  MP4")
    typer.echo("  MKV")
    typer.echo("  AVI")
    typer.echo("  MOV")

@app.command()
def check(file_path: str):
    """Check whether a media file is supported by StegX."""

    print_media_info(file_path)

@app.command()
def capacity(image_path: str):
    """Calculate how much data an image can hold."""

    try:
        info = get_image_capacity(image_path)

        print("\n--- Image Capacity Analysis ---")

        print(f"Image: {image_path}")
        print(f"Resolution: {info['width']} x {info['height']}")
        print(f"Total Pixels: {info['total_pixels']:,}")

        print(f"Available Bits: {info['available_bits']:,}")
        print(
            f"Estimated Capacity: "
            f"{format_size(info['available_bytes'])}"
        )

    except FileNotFoundError:
        print(f"\n[-] File not found: {image_path}")

    except Exception as error:
        print(f"\n[-] Could not analyze image: {error}")

@app.command()
def payload_info(file_path: str):
    """Create and inspect a StegX payload."""

    try:
        payload = create_payload(file_path)

        info = get_payload_info(payload)

        print("\n--- StegX Payload Information ---")

        print(f"Magic: {info['magic']}")
        print(f"Version: {info['version']}")
        print(f"Encrypted: {info['encrypted']}")
        print(f"Original Filename: {info['filename']}")
        print(f"Payload Size: {format_size(info['payload_size'])}")
        print(f"Header Size: {info['header_size']} bytes")
        print(f"Total StegX Payload: {format_size(len(payload))}")

    except FileNotFoundError:
        print(f"\n[-] File not found: {file_path}")

    except Exception as error:
        print(f"\n[-] Could not create payload: {error}")

@app.command()
def hide_image(
    image_path: str,
    payload_path: str,
    output_path: str = "samples/test_stego.png",
    password: str = typer.Option(
        None,
        "--password",
        "-p",
        help="Password used to encrypt the hidden payload.",
    ),
    position_key: str = typer.Option(
        None,
        "--position-key",
        "-k",
        help=(
            "Key used to generate randomized embedding "
            "positions."
        ),
    ),
):
    """Hide a file inside an image using LSB steganography."""

    try:

        result = embed_payload(
            image_path,
            payload_path,
            output_path,
            password=password,
            position_key=position_key,
        )

        print("\n[+] Payload embedded successfully!")

        print(
            f"[+] Encrypted: "
            f"{result['encrypted']}"
        )

        print(
            f"[+] Randomized positions: "
            f"{result['randomized_positions']}"
        )

        print(
            f"[+] Payload bits: "
            f"{result['payload_bits']:,}"
        )

        print(
            f"[+] Carrier capacity: "
            f"{result['available_bits']:,} bits"
        )

        print(
            f"[+] Pixels used: "
            f"{result['pixels_modified']:,}"
        )

        print(
            f"[+] Output: "
            f"{result['output_path']}"
        )

        if result["format_changed"]:

            print(
                "[!] Requested output format was unsafe "
                "for LSB steganography."
            )

            print(
                "[+] Output was automatically converted "
                "to PNG."
            )

    except FileNotFoundError as error:

        print(
            f"\n[-] File not found: {error}"
        )

    except ValueError as error:

        print(
            f"\n[-] {error}"
        )

    except Exception as error:

        print(
            f"\n[-] Embedding failed: {error}"
        )
        
@app.command()
def extract_image(
    image_path: str,
    output_directory: str = "samples/extracted",
    password: str = typer.Option(
        None,
        "--password",
        "-p",
        help="Password required for encrypted payloads.",
    ),
    position_key: str = typer.Option(
        None,
        "--position-key",
        "-k",
        help="Key used to reproduce randomized embedding positions.",
    ),
):
    """Extract a hidden StegX payload from an image."""

    try:

        result = extract_payload(
            image_path,
            output_directory,
            password=password,
            position_key=position_key,
        )

        print("\n[+] Payload extracted successfully!")

        print(
            f"[+] Original filename: "
            f"{result['filename']}"
        )

        print(
            f"[+] Payload size: "
            f"{format_size(result['payload_size'])}"
        )

        print(
            f"[+] Encrypted: "
            f"{result['encrypted']}"
        )

        print(
            f"[+] Randomized positions: "
            f"{result['randomized_positions']}"
        )

        print(
            f"[+] Recovered file: "
            f"{result['output_path']}"
        )

        content = get_displayable_content(
            result["output_path"]
        )

        if content is not None:

            print("\n--- Recovered Content ---\n")

            print(content)

        else:

            print(
                "\n[+] Binary or non-text file detected."
            )

            print(
                "[+] Content cannot be displayed directly "
                "in the terminal."
            )

    except FileNotFoundError as error:
        print(f"\n[-] File not found: {error}")

    except ValueError as error:
        print(f"\n[-] Extraction failed: {error}")

    except Exception as error:
        print(f"\n[-] Unexpected error: {error}")

@app.command()
def analyze_signature(
    image_path: str,
    position_key: str = typer.Option(
        None,
        "--position-key",
        "-k",
        help=(
            "Key used to reproduce randomized embedding "
            "positions for signature analysis."
        ),
    ),
):
    """Check whether an image contains a StegX payload."""

    try:

        result = run_signature_analysis(
            image_path,
            position_key=position_key,
        )

        print("\n--- StegX Signature Analysis ---")

        if not result["detected"]:

            print(
                "\n[-] No valid STEGX signature detected."
            )

            if position_key:

                print(
                    "[!] The position key may be incorrect."
                )

            return

        print("\n[+] STEGX signature detected!")

        print(
            f"[+] Version: "
            f"{result['version']}"
        )

        print("[+] Payload present: Yes")

        print(
            f"[+] Encrypted: "
            f"{result['encrypted']}"
        )

        print(
            f"[+] Original filename: "
            f"{result['filename']}"
        )

        print(
            f"[+] Payload size: "
            f"{format_size(result['payload_size'])}"
        )

        print(
            f"[+] Randomized positions: "
            f"{position_key is not None and position_key != ''}"
        )

    except FileNotFoundError:

        print(
            f"\n[-] File not found: {image_path}"
        )

    except ValueError as error:

        print(
            f"\n[-] Analysis failed: {error}"
        )

    except Exception as error:

        print(
            f"\n[-] Analysis failed: {error}"
        )
@app.command()
def analyze_heuristic(image_path: str):
    """Analyze an image for possible LSB steganography."""

    try:
        result = analyze_heuristics(image_path)

        print("\n--- StegX Heuristic Analysis ---\n")

        print(
            f"Total LSB bits: "
            f"{result['total_bits']:,}"
        )

        print("\nLSB Distribution:")

        print(
            f"0 bits: {result['zero_count']:,} "
            f"({result['zero_ratio']:.2f}%)"
        )

        print(
            f"1 bits: {result['one_count']:,} "
            f"({result['one_ratio']:.2f}%)"
        )

        print(
            f"\nEntropy: "
            f"{result['entropy']:.6f}"
        )

        print(
            f"Chi-square: "
            f"{result['chi_square']:.6f}"
        )

        print(
            f"Balance difference: "
            f"{result['balance_difference']:.4f}%"
        )

        print(
            f"\nSuspicion Score: "
            f"{result['suspicion_score']}/100"
        )

        print(
            f"Verdict: "
            f"{result['verdict']}"
        )

        print(
            "\n[!] Note: Heuristic analysis does not "
            "prove that steganographic content exists."
        )

    except FileNotFoundError:
        print(f"\n[-] File not found: {image_path}")

    except Exception as error:
        print(f"\n[-] Analysis failed: {error}")

@app.command()
def video_info(video_path: str):
    """Display information about a video file."""

    try:

        info = get_video_info(video_path)

        print("\n--- Video Information ---\n")

        print(
            f"Video: {info['path']}"
        )

        print(
            f"Resolution: "
            f"{info['width']} x {info['height']}"
        )

        print(
            f"FPS: "
            f"{info['fps']:.2f}"
        )

        print(
            f"Frames: "
            f"{info['frame_count']:,}"
        )

        print(
            f"Duration: "
            f"{info['duration']:.2f} seconds"
        )

        print(
            f"Codec: "
            f"{info['codec']}"
        )

        print(
            f"Extension: "
            f"{info['extension']}"
        )

    except FileNotFoundError:

        print(
            f"\n[-] File not found: "
            f"{video_path}"
        )

    except ValueError as error:

        print(
            f"\n[-] Could not analyze video: "
            f"{error}"
        )

    except Exception as error:

        print(
            f"\n[-] Unexpected error: "
            f"{error}"
        )

@app.command()
def video_capacity(video_path: str):
    """Calculate the theoretical payload capacity of a video."""

    try:

        info = get_video_capacity(video_path)

        print(
            "\n--- Video Capacity Analysis ---\n"
        )

        print(
            f"Video: {info['path']}"
        )

        print(
            f"Resolution: "
            f"{info['width']} x {info['height']}"
        )

        print(
            f"Frames: "
            f"{info['frame_count']:,}"
        )

        print(
            f"Bits per frame: "
            f"{info['bits_per_frame']:,}"
        )

        print(
            f"Total available bits: "
            f"{info['available_bits']:,}"
        )

        print(
            f"Estimated capacity: "
            f"{format_size(info['available_bytes'])}"
        )

        print(
            "\n[!] This is theoretical LSB capacity."
        )

        print(
            "[!] Actual safe capacity depends on "
            "the output codec."
        )

    except FileNotFoundError:

        print(
            f"\n[-] File not found: "
            f"{video_path}"
        )

    except Exception as error:

        print(
            f"\n[-] Could not calculate "
            f"video capacity: {error}"
        )

@app.command()
def codec_test(
    video_path: str,
    codec: str = "FFV1",
):
    """Test whether a video codec can write frames."""

    try:

        output_path = (
            f"samples/codec_test_{codec}.avi"
        )

        result = test_video_codec(
            video_path,
            output_path,
            codec,
        )

        print(
            "\n--- Video Codec Test ---\n"
        )

        print(
            f"Input: {video_path}"
        )

        print(
            f"Codec: {result['codec']}"
        )

        print(
            f"Frames written: "
            f"{result['frames_written']}"
        )

        print(
            f"Output created: "
            f"{result['file_exists']}"
        )

        print(
            f"Output file: "
            f"{result['output_path']}"
        )

        print(
            f"File size: "
            f"{format_size(result['file_size'])}"
        )

        print(
            "\n[+] Codec test completed successfully."
        )

    except Exception as error:

        print(
            f"\n[-] Codec test failed: {error}"
        )

@app.command()
def video_integrity(
    original_path: str,
    test_path: str,
):
    """Compare two videos pixel-by-pixel."""

    try:

        result = compare_video_frames(
            original_path,
            test_path,
        )

        print(
            "\n--- Video Integrity Test ---\n"
        )

        print(
            f"Original: {original_path}"
        )

        print(
            f"Test Video: {test_path}"
        )

        print(
            f"Frames Compared: "
            f"{result['frames_compared']}"
        )

        print(
            f"Different Pixel Values: "
            f"{result['different_values']:,}"
        )

        print(
            f"Maximum Difference: "
            f"{result['maximum_difference']}"
        )

        if result["identical"]:

            print(
                "\n[+] PERFECT MATCH"
            )

            print(
                "[+] All pixel values were "
                "preserved exactly."
            )

            print(
                "[+] This codec is suitable for "
                "LSB steganography."
            )

        else:

            print(
                "\n[-] PIXEL DIFFERENCES DETECTED"
            )

            print(
                "[-] This codec cannot be trusted "
                "for exact LSB preservation."
            )

    except Exception as error:

        print(
            f"\n[-] Integrity test failed: "
            f"{error}"
        )

@app.command()
def hide_video(
    video_path: str,
    payload_path: str,
    output_path: str = "samples/stego_video.avi",
    password: str = typer.Option(
        None,
        "--password",
        "-p",
        help="Password used to encrypt the hidden payload.",
    ),
    position_key: str = typer.Option(
        None,
        "--position-key",
        "-k",
        help=(
            "Key used to generate randomized "
            "embedding positions."
        ),
    ),
):
    """Hide a file inside a video using LSB steganography."""

    try:

        result = embed_video_payload(
            video_path,
            payload_path,
            output_path,
            password=password,
            position_key=position_key,
        )

        print(
            "\n[+] Payload embedded successfully!"
        )

        print(
            f"[+] Encrypted: "
            f"{result['encrypted']}"
        )

        print(
            f"[+] Randomized positions: "
            f"{result['randomized_positions']}"
        )

        print(
            f"[+] Payload bits: "
            f"{result['payload_bits']:,}"
        )

        print(
            f"[+] Carrier capacity: "
            f"{result['available_bits']:,} bits"
        )

        print(
            f"[+] Frames processed: "
            f"{result['frames_processed']:,}"
        )

        print(
            "[+] Codec: FFV1 (lossless)"
        )

        print(
            f"[+] Output: "
            f"{result['output_path']}"
        )

    except FileNotFoundError as error:

        print(
            f"\n[-] File not found: {error}"
        )

    except ValueError as error:

        print(
            f"\n[-] Embedding failed: {error}"
        )

    except Exception as error:

        print(
            f"\n[-] Unexpected error: {error}"
        )

@app.command()
def extract_video(
    video_path: str,
    output_directory: str = "samples/extracted_video",
    password: str | None = typer.Option(
        None,
        "--password",
        "-p",
        help="Password required for encrypted payloads.",
    ),
    position_key: str | None = typer.Option(
        None,
        "--position-key",
        "-k",
        help=(
            "Key used to reproduce randomized embedding "
            "positions."
        ),
    ),
):
    """Extract a hidden StegX payload from a video."""

    try:

        result = extract_video_payload(
            video_path=video_path,
            output_directory=output_directory,
            password=password,
            position_key=position_key,
        )

        print(
            "\n[+] Payload extracted successfully!"
        )

        print(
            f"[+] Original filename: "
            f"{result['filename']}"
        )

        print(
            f"[+] Payload size: "
            f"{format_size(result['payload_size'])}"
        )

        print(
            f"[+] Encrypted: "
            f"{result['encrypted']}"
        )

        print(
            f"[+] Randomized positions: "
            f"{result['randomized']}"
        )

        print(
            f"[+] Recovered file: "
            f"{result['output_path']}"
        )

        # Display readable text files directly.
        content = get_displayable_content(
            result["output_path"]
        )

        if content is not None:

            print(
                "\n--- Recovered Content ---\n"
            )

            print(content)

        else:

            print(
                "\n[+] Binary or non-text file detected."
            )

            print(
                "[+] Content cannot be displayed directly "
                "in the terminal."
            )

    except FileNotFoundError as error:

        print(
            f"\n[-] File not found: {error}"
        )

    except ValueError as error:

        print(
            f"\n[-] Extraction failed: {error}"
        )

    except Exception as error:

        print(
            f"\n[-] Unexpected error: {error}"
        )
        
@app.command()
def analyze_video_signature(
    video_path: str,
    position_key: str = typer.Option(
        None,
        "--position-key",
        "-k",
        help=(
            "Key used to reproduce randomized embedding "
            "positions for signature analysis."
        ),
    ),
):
    """
    Check whether a video contains a valid
    StegX payload signature.
    """

    try:

        result = run_video_signature_analysis(
            video_path,
            position_key=position_key,
        )

        print(
            "\n--- StegX Video Signature Analysis ---"
        )

        if not result["detected"]:

            print(
                "\n[-] No valid STEGX signature detected."
            )

            if position_key:

                print(
                    "[!] The position key may be incorrect."
                )

            return

        print(
            "\n[+] STEGX signature detected!"
        )

        print(
            f"[+] Version: "
            f"{result['version']}"
        )

        print(
            "[+] Payload present: Yes"
        )

        print(
            f"[+] Encrypted: "
            f"{result['encrypted']}"
        )

        print(
            f"[+] Original filename: "
            f"{result['filename']}"
        )

        print(
            f"[+] Payload size: "
            f"{format_size(result['payload_size'])}"
        )

        print(
            f"[+] Randomized positions: "
            f"{result.get('randomized', False)}"
        )

    except FileNotFoundError:

        print(
            f"\n[-] File not found: {video_path}"
        )

    except Exception as error:

        print(
            f"\n[-] Analysis failed: {error}"
        )
@app.command()
def analyze_video_heuristic(
    video_path: str,
):
    """Analyze a video for possible LSB steganography."""

    try:

        result = analyze_video_heuristics(
            video_path
        )

        print(
            "\n--- StegX Video Heuristic Analysis ---\n"
        )

        print(
            f"Frames analyzed: "
            f"{result['frames_analyzed']}"
        )

        print(
            f"Total LSB bits: "
            f"{result['total_bits']:,}"
        )

        print("\nLSB Distribution:")

        print(
            f"0 bits: "
            f"{result['zero_count']:,} "
            f"({result['zero_ratio']:.2f}%)"
        )

        print(
            f"1 bits: "
            f"{result['one_count']:,} "
            f"({result['one_ratio']:.2f}%)"
        )

        print(
            f"\nEntropy: "
            f"{result['entropy']:.6f}"
        )

        print(
            f"Chi-square: "
            f"{result['chi_square']:.6f}"
        )

        print(
            f"Balance difference: "
            f"{result['balance_difference']:.4f}%"
        )

        print(
            f"\nSuspicion Score: "
            f"{result['suspicion_score']}/100"
        )

        print(
            f"Verdict: "
            f"{result['verdict']}"
        )

        print(
            "\n[!] Note: Heuristic analysis does not "
            "prove that steganographic content exists."
        )

    except FileNotFoundError:

        print(
            f"\n[-] File not found: "
            f"{video_path}"
        )

    except Exception as error:

        print(
            f"\n[-] Analysis failed: "
            f"{error}"
        )
        
@app.command()
def detect(
    file_path: str,
    position_key: str = typer.Option(
        None,
        "--position-key",
        "-k",
        help=(
            "Key used to reproduce randomized embedding "
            "positions for signature detection."
        ),
    ),
):
    """
    Automatically analyze an image or video
    for StegX payloads.
    """

    try:

        if not os.path.isfile(file_path):
            raise FileNotFoundError

        media_info = get_media_info(file_path)

        print("\n--- StegX Detection Report ---\n")

        print(f"File: {file_path}")

        print(
            f"Media Type: "
            f"{media_info['media_type'].capitalize()}"
        )

        print(
            f"Format: "
            f"{media_info['name']}"
        )

        if not media_info["supported"]:

            print("\n[-] Unsupported file format.")
            return

        # ----------------------------------------
        # IMAGE DETECTION
        # ----------------------------------------

        if media_info["media_type"] == "image":

            signature_result = run_signature_analysis(
                file_path,
                position_key=position_key,
            )

            heuristic_result = analyze_heuristics(
                file_path
            )

        # ----------------------------------------
        # VIDEO DETECTION
        # ----------------------------------------

        elif media_info["media_type"] == "video":

            signature_result = run_video_signature_analysis(
                file_path,
                position_key=position_key,
            )

            heuristic_result = analyze_video_heuristics(
                file_path
            )

        else:

            print("\n[-] Unsupported media type.")
            return

        # ----------------------------------------
        # SIGNATURE RESULTS
        # ----------------------------------------

        print("\n--- Signature Analysis ---\n")

        if signature_result["detected"]:

            print("[+] STEGX signature: DETECTED")

            print(
                f"[+] Version: "
                f"{signature_result['version']}"
            )

            print(
                f"[+] Encrypted: "
                f"{signature_result['encrypted']}"
            )

            print(
                f"[+] Original filename: "
                f"{signature_result['filename']}"
            )

            print(
                f"[+] Payload size: "
                f"{format_size(signature_result['payload_size'])}"
            )

            print(
                f"[+] Randomized positions: "
                f"{signature_result.get('randomized', False)}"
            )

        else:

            print("[-] STEGX signature: NOT DETECTED")

            if position_key:

                print(
                    "[!] No valid STEGX signature was found "
                    "using the supplied position key."
                )

        # ----------------------------------------
        # HEURISTIC RESULTS
        # ----------------------------------------

        print("\n--- Heuristic Analysis ---\n")

        if media_info["media_type"] == "video":

            print(
                f"Frames analyzed: "
                f"{heuristic_result['frames_analyzed']}"
            )

        print(
            f"Suspicion Score: "
            f"{heuristic_result['suspicion_score']}/100"
        )

        print(
            f"Verdict: "
            f"{heuristic_result['verdict']}"
        )

        print(
            f"Entropy: "
            f"{heuristic_result['entropy']:.6f}"
        )

        print(
            f"Balance difference: "
            f"{heuristic_result['balance_difference']:.4f}%"
        )

        # ----------------------------------------
        # FINAL RESULT
        # ----------------------------------------

        print("\n--- Overall Result ---\n")

        if signature_result["detected"]:

            print("[+] KNOWN STEGX PAYLOAD DETECTED")

            print(
                "[+] Hidden data is confirmed "
                "by the STEGX signature."
            )

        elif heuristic_result["suspicion_score"] >= 70:

            print("[!] HIGHLY SUSPICIOUS MEDIA")

            print(
                "[!] Statistical analysis indicates "
                "possible hidden data."
            )

        elif heuristic_result["suspicion_score"] >= 40:

            print("[!] POSSIBLE SUSPICIOUS MEDIA")

            print(
                "[!] Further analysis is recommended."
            )

        else:

            print("[-] No known StegX payload detected.")

            print(
                "[!] Heuristic analysis alone cannot "
                "guarantee that hidden data is absent."
            )

    except FileNotFoundError:

        print(
            f"\n[-] File not found: {file_path}"
        )

    except ValueError as error:

        print(
            f"\n[-] Detection failed: {error}"
        )

    except Exception as error:

        print(
            f"\n[-] Detection failed: {error}"
        )

    
if __name__ == "__main__":
    app()