"""
StegX banner — CLI entry-point splash.

The wordmark resolves out of binary noise, representing hidden data
emerging from a media carrier into a readable signal.

Animation is automatically disabled for non-interactive environments
such as CI pipelines, redirected output, or when STEGX_NO_ANIM is set.
"""

from __future__ import annotations

import os
import random
import time

from rich import box
from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text


console = Console()


# ============================================================
# STEGX WORDMARK
# ============================================================

STEGX_ASCII = r"""
███████╗████████╗███████╗ ██████╗ ██╗  ██╗
██╔════╝╚══██╔══╝██╔════╝██╔════╝ ╚██╗██╔╝
███████╗   ██║   █████╗  ██║  ███╗ ╚███╔╝
╚════██║   ██║   ██╔══╝  ██║   ██║ ██╔██╗
███████║   ██║   ███████╗╚██████╔╝██╔╝ ██╗
╚══════╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝
""".strip("\n")


# ============================================================
# COLOR PALETTE
# ============================================================

CHANNEL_RED = "#FF3B5C"
CHANNEL_GREEN = "#00E5A0"
CHANNEL_BLUE = "#4B7BFF"

PAPER = "#ECEFF4"
FOG = "#7C8699"

NOISE_CHARS = "01"


# ============================================================
# COLOR UTILITIES
# ============================================================

def _blend(c1: str, c2: str, t: float) -> str:
    """
    Blend two hexadecimal colors.

    t must be between 0 and 1.
    """

    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")

    r1 = int(c1[0:2], 16)
    g1 = int(c1[2:4], 16)
    b1 = int(c1[4:6], 16)

    r2 = int(c2[0:2], 16)
    g2 = int(c2[2:4], 16)
    b2 = int(c2[4:6], 16)

    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)

    return f"#{r:02X}{g:02X}{b:02X}"


# ============================================================
# ASCII GRID
# ============================================================

def _grid() -> tuple[list[str], int, int]:
    """
    Convert the ASCII wordmark into a padded grid.
    """

    lines = STEGX_ASCII.splitlines()

    width = max(
        len(line)
        for line in lines
    )

    padded_lines = [
        line.ljust(width)
        for line in lines
    ]

    return (
        padded_lines,
        len(lines),
        width,
    )


# ============================================================
# LOGO COLOR GRADIENT
# ============================================================

def _cell_color(
    row: int,
    col: int,
    rows: int,
    cols: int,
) -> str:
    """
    Create a colorful horizontal gradient.

    RED → GREEN → BLUE
    """

    position = col / max(
        cols - 1,
        1,
    )

    # Left half:
    # RED → GREEN
    if position < 0.5:

        t = position * 2

        return _blend(
            CHANNEL_RED,
            CHANNEL_GREEN,
            t,
        )

    # Right half:
    # GREEN → BLUE
    else:

        t = (
            position - 0.5
        ) * 2

        return _blend(
            CHANNEL_GREEN,
            CHANNEL_BLUE,
            t,
        )


# ============================================================
# BANNER RENDERING
# ============================================================

def _render(
    lines: list[str],
    rows: int,
    cols: int,
    resolved: set[int],
) -> Panel:
    """
    Render the StegX wordmark.

    Resolved characters appear as the final logo.
    Unresolved characters appear as binary noise.
    """

    text = Text(
        justify="center"
    )

    for row in range(rows):

        for col in range(cols):

            character = lines[row][col]

            index = (
                row * cols
                + col
            )

            if character == " ":

                text.append(" ")

            elif index in resolved:

                text.append(
                    character,
                    style=(
                        f"bold "
                        f"{_cell_color(
                            row,
                            col,
                            rows,
                            cols,
                        )}"
                    ),
                )

            else:

                text.append(
                    random.choice(
                        NOISE_CHARS
                    ),
                    style=f"dim {FOG}",
                )

        if row < rows - 1:

            text.append("\n")

    return Panel(

        Align.center(text),

        title=(
            f"[bold {CHANNEL_RED}]"
            "STEGX"
            f"[/bold {CHANNEL_RED}]"
        ),

        subtitle=(
            f"[dim {FOG}]"
            "LSB STEGANOGRAPHY ENGINE"
            f"[/dim {FOG}]"
        ),

        box=box.HEAVY,

        border_style=CHANNEL_BLUE,

        padding=(1, 4),
    )


# ============================================================
# FEATURE TAGS
# ============================================================

def _feature_tags() -> Text:
    """
    Create the feature indicator row.
    """

    tags = Text(
        justify="center"
    )

    entries = [

        (
            "IMAGE",
            CHANNEL_RED,
        ),

        (
            "VIDEO",
            CHANNEL_GREEN,
        ),

        (
            "ENCRYPTION",
            CHANNEL_BLUE,
        ),

        (
            "DETECTION",
            PAPER,
        ),

    ]

    for index, (
        label,
        color,
    ) in enumerate(entries):

        if index:

            tags.append("   ")

        tags.append(
            "●",
            style=color,
        )

        tags.append(
            f" {label}",
            style=f"bold {PAPER}",
        )

    return tags


# ============================================================
# FOOTER
# ============================================================

def _footer() -> None:
    """
    Print the StegX identity and feature information.
    """

    console.print()

    console.print(

        Align.center(

            Text(

                "SECURE MEDIA STEGANOGRAPHY TOOLKIT",

                style=f"bold {PAPER}",

            )

        )

    )

    console.print()

    console.print(

        Align.center(
            _feature_tags()
        )

    )

    console.print()

    console.print(

        Align.center(

            Text(

                "Digital Forensics · Security Research · Steganography",

                style=f"italic {FOG}",

            )

        )

    )

    console.print()


# ============================================================
# ANIMATION CONTROL
# ============================================================

def _should_animate(
    animate: bool,
) -> bool:
    """
    Determine whether the animation should run.
    """

    if not animate:

        return False

    if os.environ.get(
        "STEGX_NO_ANIM"
    ):

        return False

    if os.environ.get(
        "CI"
    ):

        return False

    if os.environ.get(
        "NO_COLOR"
    ):

        return False

    return console.is_terminal


# ============================================================
# MAIN BANNER
# ============================================================

def show_banner(
    animate: bool = True,
) -> None:
    """
    Display the StegX CLI banner.

    The logo gradually resolves from binary noise
    into the final STEGX wordmark.
    """

    lines, rows, cols = _grid()

    cells = [

        (row, col)

        for row in range(rows)

        for col in range(cols)

        if lines[row][col] != " "

    ]

    console.print()

    # --------------------------------------------------------
    # Animated version
    # --------------------------------------------------------

    if _should_animate(animate):

        # Resolve from left to right with a small amount
        # of randomness so the animation appears more organic.

        cells.sort(

            key=lambda position: (

                position[1]

                + random.uniform(
                    -2.5,
                    2.5,
                )

            )

        )

        order = [

            row * cols + col

            for row, col in cells

        ]

        frames = 22

        step = max(
            1,
            len(order) // frames,
        )

        resolved: set[int] = set()

        with Live(

            console=console,

            refresh_per_second=40,

            transient=False,

        ) as live:

            for index in range(
                0,
                len(order),
                step,
            ):

                resolved.update(

                    order[
                        index:
                        index + step
                    ]

                )

                live.update(

                    _render(

                        lines,
                        rows,
                        cols,
                        resolved,

                    )

                )

                time.sleep(0.02)

            # Ensure every character is resolved.

            resolved.update(
                order
            )

            live.update(

                _render(

                    lines,
                    rows,
                    cols,
                    resolved,

                )

            )

    # --------------------------------------------------------
    # Static version
    # --------------------------------------------------------

    else:

        resolved = set(
            range(
                rows * cols
            )
        )

        console.print(

            _render(

                lines,
                rows,
                cols,
                resolved,

            )

        )

    _footer()


# ============================================================
# DIRECT EXECUTION TEST
# ============================================================

if __name__ == "__main__":

    show_banner()