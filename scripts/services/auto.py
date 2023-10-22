import constants.constants as constants
import multiprocessing
import pandas as pd
import pathlib
import threading
import sys

from multiprocessing import Queue
from . import configuration, scraper

# Added to make the utils module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.utils.helpers import LoggingPool

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
        # Define builders
        configuration_builder = configuration.ConfigurationBuilder()
        scraper_builder = scraper.ScraperBuilder()
        # Define engines
        config = configuration_builder.build(url)
        scraper_engine_no_headless = scraper_builder.build(
            # opts=constants.CHROME_DRIVER_NO_HEADLESS_OPTS
        )
        # Run scraper
        scraper_engine_no_headless.run(config)

        # TODO If result queue is defined, add result to queue
        # result_queue.put(pd.DataFrame([])) 
        # Dummy data
        df_dict = {key: None for key in constants.COLUMN_NAMES}
        df_dict["Company"] = "LinkedIn"
        df_dict["Position"] = "Software Engineer"
        df_dict["Date Applied"] = "01/01/2021"
        df_dict["Status"] = "Applied"
        df_dict["Portal Link"] = "https://www.linkedin.com/jobs/view/123456789/"
        df_dict["Notes"] = ""
        df = pd.DataFrame(df_dict, index=[0])
        return df

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
            # Check if any exceptions were raised by checking the existance of constants.LOG_TMP_FILENAME
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
