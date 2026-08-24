<div align="center">

```
 ██████╗▄▄▄█████▓▓█████  ▄████    ▐██▌ 
██╔════╝▓  ██▒ ▓▒▓█   ▀ ██▒ ▀█▒ ▓▓▓▓██▓
╚█████╗ ▒ ▓██░ ▒░▒███  ▒██░▄▄▄░   ▐██▌ 
 ╚═══██╗░ ▓██▓ ░ ▒▓█  ▄ ░▓█  ██▓ ▓▓▓▓██▓
██████╔╝  ▒██▒ ░ ░▒████▒░▒▓███▀▒ ▐██▌ 
╚═════╝   ▒ ░░   ░░ ▒░ ░ ░▒   ▒   ▀▀   
```

**Secure Media Steganography Toolkit for Images and Videos**

<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-4B7BFF?style=flat-square&labelColor=0B0E14" /></a>
<a href="#-license"><img src="https://img.shields.io/badge/License-Educational-00E5A0?style=flat-square&labelColor=0B0E14" /></a>
<a href="#-limitations"><img src="https://img.shields.io/badge/Status-Prototype-FF3B5C?style=flat-square&labelColor=0B0E14" /></a>
<a href="#-usage"><img src="https://img.shields.io/badge/Interface-CLI-ECEFF4?style=flat-square&labelColor=0B0E14" /></a>

**[Features](#-features) · [Install](#-install) · [Quick Start](#-quick-start) · [Commands](#-commands) · [Usage](#-usage) · [Detection](#-detection) · [Testing](#-testing) · [Architecture](#-architecture) · [Roadmap](#-roadmap)**

</div>

<br/>

Every pixel has a channel it doesn't need. StegX writes payloads into that spare bit — across images and video frames — then gives you the tools to encrypt what you hid, measure how much room you have, and prove (or disprove) that something's there at all.

<br/>

## `$ features`

<table>
<tr>
<th width="33%">Image</th>
<th width="33%">Video</th>
<th width="34%">Encryption</th>
</tr>
<tr valign="top">
<td>

LSB embedding into PNG, BMP, TIFF/TIF carriers. JPEG/WebP inputs are detected and redirected to a safe lossless output. Capacity calculation, extraction, and automatic preview of recovered text files. Optional key-based randomized pixel selection in place of sequential embedding.

</td>
<td>

Frame-by-frame LSB embedding with FFV1 lossless codec support, pixel-level integrity verification, and video info / capacity analysis.

</td>
<td>

Optional password-based encryption, applied **before** embedding — PBKDF2-HMAC-SHA256, a random 16-byte salt, 600,000 iterations, and Fernet authenticated encryption.

</td>
</tr>
</table>

<br/>

## `$ detect`

Two engines, one command. `detect` figures out whether your file is an image or video, then runs both.

<table>
<tr>
<th width="20%"></th>
<th width="40%">signature</th>
<th width="40%">heuristic</th>
</tr>
<tr valign="top">
<td><b>method</b></td>
<td>Scans for StegX's structured <code>STEGX</code> magic header</td>
<td>Measures statistical properties of the LSB plane</td>
</tr>
<tr valign="top">
<td><b>recovers</b></td>
<td>Version · encryption status · filename · payload size</td>
<td>Entropy · chi-square · bit balance · suspicion score</td>
</tr>
<tr valign="top">
<td><b>certainty</b></td>
<td>Definitive — confirms a known StegX payload</td>
<td>Probabilistic — flags anomalies, proves nothing</td>
</tr>
</table>

> Heuristic analysis never proves hidden data exists. It only surfaces statistics that *may* indicate it.

```bash
python3 -m stegx.cli detect samples/test_stego.png
```

If the payload was embedded with `--position-key`, pass the same key to `detect` so the signature scan can locate the header at its randomized offsets:

```bash
python3 -m stegx.cli detect samples/random_stego.png --position-key mysecretkey
```

<details>
<summary><b>sample report</b></summary>

```text
--- StegX Detection Report ---

File: samples/stego_video.avi
Media Type: Video
Format: AVI

--- Signature Analysis ---
[+] STEGX signature: DETECTED
[+] Version: 1
[+] Encrypted: False
[+] Original filename: secret.txt
[+] Payload size: 17 B

--- Heuristic Analysis ---
Frames analyzed: 20
Suspicion Score: 0/100
Verdict: Low suspicion

--- Overall Result ---
[+] KNOWN STEGX PAYLOAD DETECTED
[+] Hidden data is confirmed by the STEGX signature.
```

</details>

<br/>

## `$ architecture`

```
StegX
│
├── stegx/
│   ├── core/              shared primitives
│   │   ├── crypto.py          encryption · key derivation
│   │   ├── format_handler.py  media format validation
│   │   └── payload.py         payload packing · parsing
│   │
│   ├── image/              image pipeline
│   │   ├── capacity.py
│   │   ├── embed.py
│   │   └── extract.py
│   │
│   ├── video/               video pipeline
│   │   ├── analyze.py
│   │   ├── capacity.py
│   │   ├── codec_test.py
│   │   ├── detection.py
│   │   ├── embed.py
│   │   ├── extract.py
│   │   ├── heuristic.py
│   │   └── integrity.py
│   │
│   ├── analysis/            detection engines
│   │   ├── heuristic.py
│   │   └── signature.py
│   │
│   ├── utils/
│   │   └── banner.py
│   │
│   └── cli.py                entry point
│
├── samples/
├── requirements.txt
├── pyproject.toml
└── README.md
```

<br/>

## `$ requirements`

- Python 3.10+
- pip
- OpenCV-compatible video backend
- FFV1 codec support for lossless video embedding

<br/>

## `$ install`

Clone the repository:

```bash
git clone https://github.com/adicyb/StegX.git
cd StegX
```

Create and activate a virtual environment:

**Linux/macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
```

Then install StegX itself (this uses `pyproject.toml` and registers the `stegx` command on your `PATH`):

```bash
pip install -e .
```

> Installing only `requirements.txt` sets up the dependencies but does **not** install the `stegx` command. Use `pip install -e .` to get the CLI entry point.

Once installed, verify it worked:

```bash
stegx
```

<br/>

## `$ quick start`

After installation, launch StegX by running:

```bash
stegx
```

This displays the StegX banner and the available commands, grouped into Image, Video, and Detection categories.

For help with a specific command:

```bash
stegx COMMAND --help
```

For example:

```bash
stegx hide-image --help
stegx extract-image --help
stegx hide-video --help
stegx extract-video --help
```

<br/>

## `$ commands`

Running `stegx` with no arguments displays the available commands grouped by category.

### Image Commands

| Command | Description |
|---|---|
| `info` | Display information about StegX |
| `formats` | Display supported media formats |
| `check FILE` | Check whether a media file is supported |
| `capacity IMAGE` | Calculate image payload capacity |
| `payload-info FILE` | Inspect a StegX payload |
| `hide-image` | Hide a file inside an image |
| `extract-image` | Extract hidden data from an image |
| `analyze-signature` | Analyze an image for a StegX signature |
| `analyze-heuristic` | Analyze an image for possible LSB steganography |

### Video Commands

| Command | Description |
|---|---|
| `video-info VIDEO` | Display video information |
| `video-capacity VIDEO` | Calculate video payload capacity |
| `codec-test VIDEO` | Test video codec compatibility |
| `video-integrity ORIGINAL MODIFIED` | Compare original and modified video frames |
| `hide-video` | Hide a file inside a video |
| `extract-video` | Extract hidden data from a video |
| `analyze-video-signature` | Analyze a video for a StegX signature |
| `analyze-video-heuristic` | Analyze a video for possible steganographic artifacts |

### Detection

| Command | Description |
|---|---|
| `detect FILE` | Detect possible StegX payloads using signature and heuristic analysis |

<br/>

## `$ usage`

```bash
python3 -m stegx.cli info                    # project info
python3 -m stegx.cli check samples/image.png # identify media format
```

> After installing with `pip install -e .`, you can drop the `python3 -m stegx.cli` prefix and just use `stegx` (e.g. `stegx info`, `stegx check samples/image.png`).

#### image

<details open>
<summary><b>capacity &amp; payload inspection</b></summary>

```bash
python3 -m stegx.cli capacity samples/image.png
python3 -m stegx.cli payload-info secret.txt
```

</details>

<details open>
<summary><b>hide</b></summary>

```bash
python3 -m stegx.cli hide-image \
  samples/test.png \
  samples/secret.txt \
  --output-path samples/stego.png

# with encryption
python3 -m stegx.cli hide-image \
  samples/test.png \
  samples/secret.txt \
  --output-path samples/encrypted_stego.png \
  --password mypassword
```

**Randomized pixel selection.** By default, StegX embeds sequentially, starting from the first pixel. Passing `--position-key` instead derives a pixel-visitation order from the key and scatters the payload across that pseudorandom path, rather than writing to a contiguous run of pixels. This makes the payload's location dependent on the key rather than a fixed, predictable start point, which is useful for classroom exercises on the limitations of naive sequential LSB steganalysis.

```bash
python3 -m stegx.cli hide-image \
  samples/test.png \
  samples/secret.txt \
  --output-path samples/random_stego.png \
  --position-key mysecretkey

# randomized placement + encryption can be combined
python3 -m stegx.cli hide-image \
  samples/test.png \
  samples/secret.txt \
  --output-path samples/random_encrypted_stego.png \
  --position-key mysecretkey \
  --password mypassword
```

> The position key only determines *where* bits are written — it is not a substitute for `--password` encryption of the payload contents. Use both together for randomized placement of encrypted data.

</details>

<details open>
<summary><b>extract</b></summary>

```bash
python3 -m stegx.cli extract-image samples/stego.png

# encrypted payloads
python3 -m stegx.cli extract-image \
  samples/encrypted_stego.png \
  --password mypassword
```

If the payload was hidden with `--position-key`, the same key must be supplied on extraction to reconstruct the pixel-visitation order:

```bash
python3 -m stegx.cli extract-image \
  samples/random_stego.png \
  --position-key mysecretkey

# randomized placement + encryption
python3 -m stegx.cli extract-image \
  samples/random_encrypted_stego.png \
  --position-key mysecretkey \
  --password mypassword
```

> Recovered text files are printed to the terminal automatically.

</details>

#### video

> ⚠️ **Important:** LSB-based video embedding requires pixel values to survive encoding. StegX currently uses the FFV1 lossless codec for stego video output. Converting the resulting video to MP4/H.264, uploading it to a platform that recompresses video, or transcoding it may destroy the hidden payload.

<details open>
<summary><b>info, capacity &amp; codec</b></summary>

```bash
python3 -m stegx.cli video-info samples/test.mp4
python3 -m stegx.cli video-capacity samples/test.mp4
python3 -m stegx.cli codec-test samples/test.mp4
```

> Video capacity is theoretical — actual usable capacity depends on whether the output codec preserves pixel values. StegX currently targets **FFV1**, a lossless codec suitable for LSB modification.

</details>

<details open>
<summary><b>integrity check</b></summary>

```bash
python3 -m stegx.cli video-integrity \
  samples/test.mp4 \
  samples/codec_test_FFV1.avi
```

A perfect match means pixel values survived the codec round-trip.

</details>

<details open>
<summary><b>hide &amp; extract</b></summary>

```bash
python3 -m stegx.cli hide-video \
  samples/test.mp4 \
  samples/secret.txt \
  --output-path samples/stego_video.avi \
  --password mypassword    # optional

python3 -m stegx.cli extract-video \
  samples/stego_video.avi \
  --password mypassword    # if encrypted
```

> `--position-key` randomized pixel selection is currently image-only; video embedding remains sequential. See [Roadmap](#-roadmap).

</details>

<br/>

## `$ payload format`

```text
┌───────────────┐
│ MAGIC: STEGX  │  5 bytes
├───────────────┤
│ VERSION       │  1 byte
├───────────────┤
│ FLAGS         │  1 byte
├───────────────┤
│ FILENAME LEN  │  2 bytes
├───────────────┤
│ FILENAME      │  variable
├───────────────┤
│ PAYLOAD SIZE  │  8 bytes
├───────────────┤
│ SALT          │  16 bytes (if encrypted)
├───────────────┤
│ PAYLOAD DATA  │  variable
└───────────────┘
```

This header makes signature detection and structured extraction possible. It identifies the payload format, encryption state, original filename, and encrypted payload size so StegX knows exactly how much data to recover. When `--position-key` is used, the header and payload bits are written across a key-derived pseudorandom pixel order instead of sequential pixels; the same key is required to walk that order again during detection and extraction.

<details>
<summary><b>detection flow</b></summary>

```text
                    ┌─────────────────┐
                    │   Media File    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Media Detection │
                    └────────┬────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌────────────────┐      ┌────────────────┐
        │ Signature Scan │      │ Heuristic Scan │
        └───────┬────────┘      └───────┬────────┘
                ▼                       ▼
        STEGX Signature?         LSB Statistics
                └───────────┬───────────┘
                             ▼
                  ┌───────────────────┐
                  │  Detection Result │
                  └───────────────────┘
```

</details>

<br/>

## `$ testing`

Run the complete test suite using:

```bash
pytest -v
```

The project currently includes tests for:

- Payload creation and validation
- Encryption and decryption
- Incorrect password handling
- Randomized embedding positions
- Image embedding and extraction
- Video embedding and extraction
- Encrypted and randomized workflows

Current test suite: **22 tests passing**.

<br/>

## `$ limitations`

- Image embedding defaults to sequential 1-bit LSB; `--position-key` enables key-derived randomized pixel selection as an alternative, but the order is still a single deterministic path per key, not a cryptographically secure PRP
- Randomized pixel selection (`--position-key`) is image-only; video embedding is still sequential
- Video embedding requires a lossless codec (FFV1) — any recompression or transcode (e.g. to MP4/H.264) can destroy the payload
- Heuristic detection is statistical, never conclusive
- Signature detection only recognizes StegX's own payload format, and requires the correct `--position-key` to locate a randomized payload
- Video capacity figures are theoretical and codec-dependent
- Built for local experimentation and education, not production use

<br/>

## `$ roadmap`

- [x] Key-based randomized pixel selection *(images)*
- [ ] Key-based randomized pixel selection *(video)*
- [ ] Multi-bit embedding options
- [ ] Additional image formats
- [ ] Audio steganography
- [ ] Advanced steganalysis techniques
- [ ] ML-based steganography detection
- [ ] GUI / web interface
- [ ] Batch media analysis
- [ ] Automated report generation

<br/>

---

<div align="center">
<sub>

Built for cybersecurity education, digital forensics research, and steganography experimentation.
**Not to be used for concealing malicious content or evading legitimate security controls.**

<br/><br/>

**Aditya Khandelwal** — Cybersecurity · Digital Forensics · Security Research
Educational / research use · ⭐ star the repo if StegX was useful to you

</sub>
</div>