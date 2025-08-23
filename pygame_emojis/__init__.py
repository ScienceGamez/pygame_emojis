"""Emoji support for the game."""
import logging
from pathlib import Path
import emoji
import io

import pygame

from pygame_emojis.emojis_data.download import _EMOJIS_DIR
from pygame_emojis.emojis_data.svg import cairosvg, cairo_installed

logger = logging.getLogger("pygame_emojis")


class EmojiNotFound(Exception):
    ...


def find_code(emoji_: str) -> list[str]:
    """Find the unicode values of the emoji.

    Return a list with all the unicodes.
    """
    # Convert the emoji to a byte str of the emoji
    logger.debug(f"{emoji_}")
    emoji_ = emoji.emojize(emoji_)
    logger.debug(f"{bytes(emoji_, 'utf-8')=}")
    # Convert the byte str to the hexadecimal code

    return [f"{ord(e):X}" for e in emoji_]

def find_emoji(emoji_: str, extension: str = "svg" if cairo_installed else "png") -> Path | None:
    """Find an emoji image file (regardless of extension) based on the emoji.

    It uses the following method:

    * Converts the emoji to Unicode codepoints.
    * Searches for files whose names start with the codepoints.
    * If none are found, shortens the code progressively and retries.
    """

    try:
        code_list = find_code(emoji_)
    except Exception as e:
        raise EmojiNotFound(emoji_) from e
    logger.debug(f"{code_list=}")

    while code_list:

        code = "-".join(code_list)
        # Check for the file matching code list
        target_file = _EMOJIS_DIR / f"{code}.{extension}"

        if target_file.exists():
            return target_file

        # Check for more complex files
        possible_files = [f for f in _EMOJIS_DIR.rglob(f"{code}*.{extension}")]
        if possible_files:
            return possible_files[0]

        # Check with less complex code name
        code_list.pop()

    return None


def load_emoji(
    emoji_: str, size: tuple[int, int] | int = None
) -> pygame.Surface:
    """Load a surface corresponding to the emoji.

    If not found, raise a FileNotFoundError.
    """

    file = find_emoji(emoji_)
    logger.debug(f"{file=}")
    if file is not None:
        return emoji_to_surface(file, size)
    else:
        raise FileNotFoundError(f"No file available for emoji {emoji_}")

def load_svg(filename: str, size: tuple[int, int] | int = None) -> pygame.Surface:
    """Handles loading and converting SVG files."""

    if not cairo_installed:
        raise ImportError("CairoSVG is not installed or not available. Cannot load SVG files.")
    
    kwargs = {}

    if size:
        kwargs["parent_width"] = size if isinstance(size, int) else size[0]
        kwargs["parent_height"] = size if isinstance(size, int) else size[1]

    new_bytes = cairosvg.svg2png(url=str(filename), **kwargs)
    byte_io = io.BytesIO(new_bytes)
    return pygame.image.load(byte_io)


def load_png(filename: str, size: tuple[int, int] | int = None) -> pygame.Surface:
    """Handles loading PNG files."""
    image = pygame.image.load(filename)
    
    if size:
        if isinstance(size, int):
            width = height = size
        elif isinstance(size, tuple):
            width, height = size
        image = pygame.transform.scale(image, (width, height))
    
    return image

def emoji_to_surface(filename: Path, size: tuple[int, int] | int = None) -> pygame.Surface:
    """Load an image (PNG or SVG) and scale it based on the input size."""

    # Check the file extension and call the appropriate sub-function
    if filename.suffix == '.png':
        return load_png(filename, size)
    elif filename.suffix == '.svg':
        return load_svg(filename, size)
    else:
        raise ValueError(f"Image file must be a .png or .svg file, got {filename.suffix}")