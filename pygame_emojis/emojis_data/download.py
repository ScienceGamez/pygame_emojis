from io import BytesIO
import pathlib
from zipfile import ZipFile
from urllib.request import urlopen
from pygame_emojis.emojis_data.svg import cairo_installed


_EMOJIS_DIR: pathlib.Path = pathlib.Path(__file__).parent / ("svg" if cairo_installed else "png")


def download():
    base_url = "https://github.com/hfg-gmuend/openmoji/releases/latest/download/"

    zip_url = f"{base_url}{'openmoji-svg-color.zip' if cairo_installed else 'openmoji-618x618-color.zip'}"

    """Download the emojis from openmoji."""
    print("[pygame_emojis] Download the zip file from ", zip_url)
    resp = urlopen(zip_url)
    zipfile = ZipFile(BytesIO(resp.read()))

    print("[pygame_emojis] Extract the zip file to ", _EMOJIS_DIR)
    zipfile.extractall(_EMOJIS_DIR)


if __name__ == "__main__":
    # Download the raw data
    download()
