import pandas as pd
import constants.constants as constants

from . import configuration, scraper

class AutoService:
    """
    Service for automatically generating job entries in
    the source CSV file from a url
    """

    @staticmethod
    def run(url: str) -> pd.DataFrame:
        """
        @param url: URL to scrape job application data from
        @return: Pandas DataFrame containing a single row job entry 
        """
        # Build configuration for url
        configuration_builder = configuration.ConfigurationBuilder()
        config = configuration_builder.build(url)
        # Build scraper
        scraper_builder = scraper.ScraperBuilder()
        scraper_engine_no_headless = scraper_builder.build(opts=constants.CHROME_DRIVER_NO_HEADLESS_OPTS)
        # Run scraper
        scraper_engine_no_headless.run(config)