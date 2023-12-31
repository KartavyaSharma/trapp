import constants

from . import configuration, vault
from .redis import lock as lk
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class ScraperEngine:
    """
    Selenium Chrome driver wrapper class. Creates a Chrome driver instance
    with custom options and runs selenium on a given URL with a config.
    """

    def __init__(
        self,
        options: Options,
        driver: webdriver.Chrome = None,
        headed_support: bool = True,
    ):
        """
        Create scraper engine instance.

        @param options: Options to pass to Chrome driver
        @param driver: Existing Chrome driver instance
        @param headed_support: Whether system supports headed mode
        """
        self.options = options
        self.driver = driver
        self.service = Service(executable_path=constants.CHROME_DRIVER_EXECUTABLE)
        self.headed_support = headed_support

    def __getattribute__(self, __name: str) -> any:
        if __name != "service":
            return super().__getattribute__(__name)

    def create_driver(self, custom_driver: any = None) -> None:
        """
        Create Chrome driver instance.

        @param custom_driver: Optional custom driver
        """
        if custom_driver:
            self.driver = custom_driver
        else:
            self.driver = webdriver.Chrome(options=self.options, service=self.service)

    def run(
        self,
        config: configuration.ConfigurationContainer = None,
        auth_engine: any = None,
    ) -> None:
        """
        Run scraper on a given URL with a config.

        @param config: Configuration object for scraper containing the platform, cookies, etc.
        @param auth_engine: Optional authentication engine to use for authentication
        @return Scraped data for platform
        """
        lock = lk.Lock(client=config.redis, name=config.platform.name)
        print(f"Scraping {config.platform.url}...")
        config.inject_driver(driver=self.driver)
        while True:
            if lock.acquire():
                # Check if authenticated
                if not vault.VaultService.isAuthenticated(
                    config.platform, headed_support=auth_engine.headed_support
                ):
                    vault.VaultService.authenticate(
                        config.platform, auth_engine=auth_engine
                    )
                lock.release()
                break
        return config.platform.scrape_wrapper()


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

    def setup_options(
        self, default=True, opts: list[str] = [], user_opts: Options = None
    ) -> Options:
        """
        Setup Chrome driver options.

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

    def build(
        self,
        opts: list[str] = [],
        delay_driver_build: bool = False,
        headed_support: bool = True,
    ) -> ScraperEngine:
        """
        Scraper engine factory build method.

        @param opts: List of options to add to Chrome driver
        @return: ScraperEngine instance
        """
        options = self.setup_options(default=not bool(opts), opts=opts)
        engine = ScraperEngine(options=options, headed_support=headed_support)
        if not delay_driver_build:
            engine.create_driver()
        return engine
