import constants.constants as constants
import datetime
import multiprocessing
import pandas as pd
import pathlib
import threading
import sys

from . import configuration, scraper
from scripts.models import entry, status

# Added to make the utils module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.utils.helpers import LoggingPool, has_gui

class AutoService:
    """
    Service for automatically generating job entries in
    the source CSV file from a url
    """

    thread_local = threading.local()

    @staticmethod
    def run(url: str) -> pd.DataFrame:
        """
        @param url: URL to scrape job application data from
        @param result_queue: Queue to store multiprocessing results in (optional)
        @return: Pandas DataFrame containing a single row job entry 
        """
        # Check if GUI is supported
        gui_support = has_gui()
        # Define builders
        configuration_builder = configuration.ConfigurationBuilder()
        scraper_builder = scraper.ScraperBuilder()
        # Create configuration and scraper engine
        config = configuration_builder.build(url)
        scraper_engine = scraper_builder.build()
        # Partially build the auth engine
        auth_engine = scraper_builder.build(
            opts=constants.CHROME_DRIVER_NO_HEADLESS_OPTS if gui_support else [], # Run in non-headless mode 
            delay_driver_build=True,
            headed_support=gui_support
        )
        # Run scraper
        (title, company, location, post_url) = scraper_engine.run(config, auth_engine=auth_engine)
        
        # Create entry
        new_entry = entry.Entry(
            company=company,
            position=title,
            date_applied=datetime.datetime.now(),
            status=status.Status.INIT,
            link=post_url,
            notes=f"{location}"
        )

        # Get dataframe
        return new_entry.create_dataframe()


    @staticmethod
    def batch_run(urls: list[str]) -> pd.DataFrame:
        """
        @param urls: List of URLs to scrape job application data from
        @return: Pandas DataFrame containing multiple job entries
        """
        # Enable logging
        multiprocessing.log_to_stderr()
        # Define worker pool
        pool = LoggingPool(processes=min(len(urls), constants.MAX_WORKERS))
        # Get results
        results, final = [], []
        # Start worker functions
        for url in urls:
            results.append(pool.apply_async(AutoService.run, args=(url,)))

        # Wait for all workers to finish
        pool.close()
        pool.join()

        for result in results:
            try:
                r = result.get()
            except Exception as e:
                continue
            if not isinstance(r, Exception):
                final.append(r)

        # Terminate pool
        pool.terminate()

        # Delete thread local
        del AutoService.thread_local

        # Return results
        return pd.concat(final, ignore_index=True)
