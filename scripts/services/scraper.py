from typing import Any
import pandas

import scripts.services.auth as auth
import constants.constants as constants

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class ScraperBuilder:

    def __init__(self, options: Options = None):
        """
        @param options: Options to pass to Chrome driver
        """
        self.options = options if options else Options()
        self.engine = None

    def setup_options(self, default=True, opts: list[str] = []) -> None:
        """
        @param default: Whether to use default options
        @param opts: List of options to add to Chrome driver
        """    
        opts = opts if not default else [*constants.CHROME_DRIVER_DEFAULT_OPTS]
        for arg in opts:
            print(arg)
            self.options.add_argument(arg)

    def build(self, opts: list[str] = []) -> webdriver.Chrome:
        """
        @param opts: List of options to add to Chrome driver
        """
        self.setup_options(default=bool(opts), opts=opts)
        self.engine = ScraperEngine(self.options)
        return self.engine.create_driver()
    
    @staticmethod
    def run(driver: webdriver.Chrome, url: str, config: any = None) -> None:
        """
        @param config: Configuration object for scraper (cookies etc.)
        """
        driver.get(url)

class ScraperEngine:

    def __init__(self, options: Options, driver: webdriver.Chrome = None):
        """
        @param options: Options to pass to Chrome driver
        @param driver: Existing Chrome driver instance
        """
        self.options = options
        self.driver = driver
        self.service = Service(executable_path=constants.CHROME_DRIVER_EXECUTABLE)

    def __getattribute__(self, __name: str) -> Any:
        if __name != "service":
            return super().__getattribute__(__name)

    def create_driver(self) -> None:
        """
        Create Chrome driver instance
        """
        if not self.driver:
            self.driver = webdriver.Chrome(
                options=self.options, service=self.service
            )
        return self.driver


class ConfigurationBuilder:
    pass


def main(url: str) -> pandas.DataFrame:
    builder = ScraperBuilder()
    # Run scraper
    ScraperBuilder.run(builder.build(), url)
