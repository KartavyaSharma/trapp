from typing import Any
import pandas

import scripts.services.auth as auth
import constants.constants as constants

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class ScraperBuilder:
    pass


class ScraperEngine:

    def __init__(self, options: Options, driver: webdriver.Chrome = None):
        self.options = options
        self.driver = driver
        self.service = Service(
            executable_path=constants.CHROME_DRIVER_EXECUTABLE)

    def __getattribute__(self, __name: str) -> Any:
        if __name != "service":
            return super().__getattribute__(__name)

    def create_driver(self) -> None:
        if not self.driver:
            self.driver = webdriver.Chrome(
                options=self.options, service=self.service
            )


class ConfigurationBuilder:
    pass


def main(url: str) -> pandas.DataFrame:
    scraper_opts = Options()
    scraper_opts.headless = False
    scraper_engine = ScraperEngine(scraper_opts)
    scraper_engine.create_driver()
    scraper_engine.driver.get(url)
