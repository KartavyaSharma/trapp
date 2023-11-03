import pathlib
import sys

from ..services.platforms.linkedin import LinkenIn
from ..services.platforms.handshake import Handshake
from ..services.platforms.greenhouse import GreenHouse

# Added to make the utils module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.models.platform import Platform


class PlatformBuilder:
    """
    Build platform instances
    """

    platforms = {
        "LinkedIn".lower(): LinkenIn,
        "Handshake".lower(): Handshake,
        "GreenHouse".lower(): GreenHouse,
    }

    @staticmethod
    def build(platform_name: str, url: str) -> Platform:
        """
        Build platform instance from URL
        """
        platform_name = platform_name.lower()
        try:
            return PlatformBuilder.platforms[platform_name](url)
        except KeyError:
            raise NotImplementedError
