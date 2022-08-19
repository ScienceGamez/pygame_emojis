from io import BytesIO
import pathlib
from zipfile import ZipFile
from urllib.request import urlopen


_SVG_DIR: pathlib.Path = pathlib.Path(__file__).parent / "svg"


def download(
    zip_url="https://github.com/hfg-gmuend/openmoji/releases/latest/download/openmoji-svg-color.zip",
):
    """Download the emojis from openmoji."""
    print("[pygame_emojis] Download the zip file from ", zip_url)
    resp = urlopen(zip_url)
    zipfile = ZipFile(BytesIO(resp.read()))

    print("[pygame_emojis] Extract the zip file to ", _SVG_DIR)
    zipfile.extractall(_SVG_DIR)


if __name__ == "__main__":
    # Dowload the raw data
    download()
