import pathlib
import sys
import constants.constants as constants

from selenium import webdriver
from ..models.platform import Platform
from .platform import PlatformBuilder

# Added to make the utils module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.utils.helpers import get_root_from_url
from scripts.utils.errors import InvalidURLError

class ConfigurationContainer:
    """
    Generates configurations for specific platforms
    """

    def __init__(self, platform: Platform):
        self.platform = platform

    def inject_driver(self, driver: webdriver.Chrome) -> None:
        """
        Set driver for platform associated with configuration

        @param selenium_driver: Chrome driver instance
        """
        self.platform.set_driver(driver)


class ConfigurationBuilder:
    """
    Configuration builder factory class
    """

    def get_platform(self, url: str) -> Platform:
        """
        Get platform from URL
        """
        builder = PlatformBuilder()
        platform_root = get_root_from_url(url)
        for url_part in platform_root.split("."):
            if url_part in constants.PLATFORM_MAP:
                return builder.build(constants.PLATFORM_MAP[url_part], url)
        raise InvalidURLError(url)

    def build(self, url: str) -> ConfigurationContainer:
        """
        Build configuration container
        """
        return ConfigurationContainer(self.get_platform(url))
