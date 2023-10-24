from typing import Any
import constants.constants as constants
import datetime
import multiprocessing
import pandas as pd
import pathlib
import threading
import sys

from . import configuration, scraper
from scripts.models import entry, status
from selenium import webdriver

# Added to make the utils module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.utils.helpers import has_gui, check_xvfb
from scripts.utils.threader import LoggingPool

class AutoService(object):
    """
    Service for automatically generating job entries in
    the source CSV file from a url
    """

    thread_local = threading.local()

    def __init__(self):
        # Check if GUI is supported
        self.gui_support = has_gui()
        if not self.gui_support:
            print("GUI not supported on this system, checking for additional dependencies")
            check_xvfb()
            from pyvirtualdisplay import Display # Should be installed in check_xvfb()
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

    def __getattribute__(self, __name: str) -> Any:
        if __name != "thread_local":
            return super().__getattribute__(__name)
    
    def __del__(self):
        if not self.gui_support:
            self.display.stop()

    @staticmethod
    def run(url: str, gui_support: bool = True) -> pd.DataFrame:
        """
        @param url: URL to scrape job application data from
        @param result_queue: Queue to store multiprocessing results in (optional)
        @return: Pandas DataFrame containing a single row job entry 
        """
        # Define builders
        configuration_builder = configuration.ConfigurationBuilder()
        scraper_builder = scraper.ScraperBuilder()
        # Create configuration and scraper engine
        config = configuration_builder.build(url)
        scraper_engine = scraper_builder.build()
        # Partially build the auth engine
        auth_opts = constants.CHROME_DRIVER_NO_HEADLESS_OPTS 
        auth_engine = scraper_builder.build(
            opts=auth_opts, # Run in non-headless mode 
            delay_driver_build=True,
            headed_support=gui_support,
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
    def batch_run(urls: list[str], gui_support: bool = True) -> pd.DataFrame:
        """
        @param urls: List of URLs to scrape job application data from
        @return: Pandas DataFrame containing multiple job entries
        """
        # Remove possible duplicates
        if len(urls) != len(set(urls)):
            print("Duplicate URLs detected, removing duplicates...")
        urls = set(urls)
        # Enable logging
        multiprocessing.log_to_stderr()
        # Define worker pool
        pool = LoggingPool(processes=min(len(urls), constants.MAX_WORKERS))
        # Get results
        results, final = [], []
        # Start worker functions
        for url in urls:
            results.append(pool.apply_async(AutoService.run, args=(url, gui_support,)))

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
