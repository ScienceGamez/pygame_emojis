"""Emoji support for the game."""

from .download import _SVG_DIR, download


if not _SVG_DIR.exists():
    _SVG_DIR.mkdir()
    download()
