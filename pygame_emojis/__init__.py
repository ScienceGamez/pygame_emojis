"""Emoji support for the game."""
import logging
from pathlib import Path
import emoji
import cairosvg
import io

import pygame

from pygame_emojis.emojis_data.download import _SVG_DIR

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


def find_svg(emoji_: str) -> Path:
    """Find the svg file tha can be used.

    It uses the follwing method:

    * Find the unicode values of the emoji
    * Tries to find files corresponding to the given unicode values
    * If a file or more are found, return the files
    * Otherwise try to find a file that matches less unicode values
    * repeat until there are no values that were matched
    """

    try:
        code_list = find_code(emoji_)
    except Exception as e:
        raise EmojiNotFound(emoji_) from e
    logger.debug(f"{code_list=}")

    while code_list:

        code = "-".join(code_list)
        # Check for the file matching code list
        target_file = _SVG_DIR.with_name(f"{code}.svg")
        if target_file.exists():
            return target_file

        # Check for more complex files
        possible_files = [f for f in _SVG_DIR.rglob(f"{code}*.svg")]
        if possible_files:
            return possible_files[0]

        # Check with less complex code name
        code_list.pop()

    # Return an empty list if no file was found
    return None


def load_emoji(
    emoji_: str, size: tuple[int, int] | int = None
) -> pygame.Surface:
    """Load a surface corresponding to the emoji.

    If not found, raise a FileNotFoundError.
    """

    file = find_svg(emoji_)
    logger.debug(f"{file=}")
    if file is not None:
        return load_svg(file, size)
    else:
        raise FileNotFoundError(f"No file available for emoji {emoji_}")


def load_svg(filename, size: tuple[int, int] | int = None) -> pygame.Surface:
    """Load a svg image with cairosvg."""
    kwargs = {}
    if size:
        kwargs["parent_width"] = size if isinstance(size, int) else size[0]
        kwargs["parent_height"] = size if isinstance(size, int) else size[1]

    new_bites = cairosvg.svg2png(url=str(filename), **kwargs)
    byte_io = io.BytesIO(new_bites)
    return pygame.image.load(byte_io)
