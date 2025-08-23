"""Emoji support for the game."""

from .download import _EMOJIS_DIR, download


if not _EMOJIS_DIR.exists():
    _EMOJIS_DIR.mkdir(parents=True)
    download()
