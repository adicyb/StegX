from rich.console import Console

console = Console()


def show_banner():
    banner = r"""
   _____ _______ ______ _____  __
  / ____|__   __|  ____/ ____| \ \
 | (___    | |  | |__ | |  __   \ \
  \___ \   | |  |  __|| | |_ |   > >
  ____) |  | |  | |___| |__| |  / /
 |_____/   |_|  |______\_____| /_/

       Secure Media Steganography Toolkit
    """

    console.print(banner, style="bold cyan")

    console.print(
        "[bold yellow]⚠ Format Notice:[/bold yellow]\n"
        "Recommended image carriers: PNG, BMP, TIFF\n"
        "Lossy formats such as JPG/JPEG may not preserve LSB data.\n"
        "StegX will validate formats and apply safe handling when possible.\n"
    )