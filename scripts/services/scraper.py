import constants.constants as constants

from . import configuration
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from typing import Any


class ScraperEngine:
    """
    Selenium Chrome driver wrapper class. Creates a Chrome driver instance
    with custom options and runs selenium on a given URL with a config.
    """

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
        self.driver = webdriver.Chrome(
            options=self.options, service=self.service
        )

    def run(self, config: configuration.ConfigurationContainer = None) -> None:
        """
        @param config: Configuration object for scraper containing the platform, cookies, etc.
        """
        config.inject_driver(self.driver)
        config.platform.init()
        # if not config.authenticated:
        #     config.platform.login()
        return config.platform.scrape_job()


class ScraperBuilder:
    """
    Factory class for creating Chrome driver instances with custom options.
    Entry point through the build() method.

    Example usage:
    builder = ScraperBuilder()
    scraper = builder.build()
    scraper.run("<url>")

    Example usage to run w/o headless mode:
    builder = ScraperBuilder()
    scraper_no_headless = builder.build(opts=constants.CHROME_DRIVER_NO_HEADLESS_OPTS)
    scraper_no_headless.run("<url>")
    """

    def setup_options(self, default=True, opts: list[str] = [], user_opts: Options = None) -> Options:
        """
        @param default: Whether to use default options
        @param opts: List of options to add to Chrome driver
        @param user_opts: User defined options
        @return: Options instance
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
        @return: ScraperEngine instance
        """
        options = self.setup_options(default=not bool(opts), opts=opts)
        engine = ScraperEngine(options=options)
        engine.create_driver()
        return engine