import pandas as pd
import constants.constants as constants
import multiprocessing

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
        # Define builders
        configuration_builder = configuration.ConfigurationBuilder()
        scraper_builder = scraper.ScraperBuilder()
        # Define engines
        config = configuration_builder.build(url)
        scraper_engine_no_headless = scraper_builder.build(opts=constants.CHROME_DRIVER_NO_HEADLESS_OPTS)
        # Run scraper
        scraper_engine_no_headless.run(config)

    @staticmethod
    def batch_run(urls: list[str]) -> pd.DataFrame:
        """
        @param urls: List of URLs to scrape job application data from
        @return: Pandas DataFrame containing multiple job entries
        """
        pool = multiprocessing.Pool(4)
        dfs = list(pool.map(AutoService.run, urls))
        # Concatenate all dataframes
        df = pd.concat(dfs, ignore_index=True)
        return df
