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


def find_svg(emoji_: str) -> list[Path]:
    """Find the svg file tha can be used."""

    try:
        code_list = find_code(emoji_)
    except Exception as e:
        raise EmojiNotFound(emoji_) from e
    logger.debug(f"{code_list=}")
    code = "-".join(code_list)
    possible_files = [f for f in _SVG_DIR.rglob(f"{code}*.svg")]
    return possible_files


def load_emoji(
    emoji_: str, size: tuple[int, int] | int = None
) -> pygame.Surface:
    """Load a surface corresponding to the emoji."""

    possible_files = find_svg(emoji_)
    logger.debug(f"{possible_files=}")
    if possible_files:
        return load_svg(possible_files[-1], size)
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


if __name__ == "__main__":
    # This will list all the files availabe for all the emojis known by emoji package
    print(_SVG_DIR)

    for e, v in emoji.EMOJI_DATA.items():
        print(e, v)

        try:
            print(e, find_code(e))
            print("Files: ", find_svg(e))
        except:
            print("Could not translate")
        print(f_name := "{}*.svg".format(e))
        print("Files v2: ", [f for f in _SVG_DIR.rglob(f_name)])
