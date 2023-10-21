from typing import Any
import pandas

import scripts.services.auth as auth
import constants.constants as constants

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


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

    def run(self, url: str, config: any = None) -> None:
        """
        @param config: Configuration object for scraper (cookies etc.)
        """
        self.driver.get(url)


class ScraperBuilder:

    def setup_options(self, default=True, opts: list[str] = [], user_opts: Options = None) -> Options:
        """
        @param default: Whether to use default options
        @param opts: List of options to add to Chrome driver
        """
        if user_opts:
            return user_opts
        options = Options() 
        opts = opts if not default else [*constants.CHROME_DRIVER_DEFAULT_OPTS]
        if opts != constants.CHROME_DRIVER_NO_HEADLESS_OPTS:
            for arg in opts:
                options.add_argument(arg)
        return options

    def build(self, opts: list[str] = []) -> ScraperEngine:
        """
        @param opts: List of options to add to Chrome driver
        """
        options = self.setup_options(default=not bool(opts), opts=opts)
        engine = ScraperEngine(options)
        engine.create_driver()
        return engine


class ConfigurationBuilder:
    pass


def main(url: str) -> pandas.DataFrame:
    # Build scraper
    builder = ScraperBuilder()
    scraper = builder.build()  # Build scraper
    scraper.run(url)  # Run scraper
    # Build no headless scraper
    scraper_no_headless = builder.build(opts=constants.CHROME_DRIVER_NO_HEADLESS_OPTS)
    scraper_no_headless.run(url)  # Run scraper
    # Build incognito scraper
    scraper_incognito = builder.build(opts=["--incognito"])
    scraper_incognito.run(url)  # Run scraper

    
