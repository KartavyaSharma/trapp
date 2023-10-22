import constants.constants as constants
import pandas as pd
import threading

from multiprocessing.pool import ThreadPool
from multiprocessing import Queue
from . import configuration, scraper

class AutoService:
    """
    Service for automatically generating job entries in
    the source CSV file from a url
    """

    thread_local = threading.local()

    @staticmethod
    def run(url: str, result_queue: Queue = None) -> pd.DataFrame:
        """
        @param url: URL to scrape job application data from
        @param result_queue: Queue to store multiprocessing results in (optional)
        @return: Pandas DataFrame containing a single row job entry 
        """
        try:
            # Define builders
            configuration_builder = configuration.ConfigurationBuilder()
            scraper_builder = scraper.ScraperBuilder()
            # Define engines
            config = configuration_builder.build(url)
            scraper_engine_no_headless = scraper_builder.build(opts=constants.CHROME_DRIVER_NO_HEADLESS_OPTS)
            # Run scraper
            scraper_engine_no_headless.run(config)
            
            # TODO If result queue is defined, add result to queue
            result_queue.put(pd.DataFrame({}))
        except Exception as e:
            # Add exception to queue if queue is defined
            if result_queue:
                result_queue.put(e)
            else:
                raise e

    @staticmethod
    def batch_run(urls: list[str]) -> pd.DataFrame:
        """
        @param urls: List of URLs to scrape job application data from
        @return: Pandas DataFrame containing multiple job entries
        """
        # Define worker pool
        pool = ThreadPool(processes=min(len(urls), 4))
        # Define result queue
        result_queue = Queue()
        # Start worker functions
        for url in urls:
            pool.apply_async(AutoService.run, args=(url, result_queue)) 

        # Wait for all workers to finish
        pool.close()
        pool.join()

        # Get results from queue
        results, exceptions = [], []

        for _ in urls:
            result = result_queue.get()
            if isinstance(result, Exception):
                exceptions.append(result)
            else:
                results.append(result)
        
        # Raise exceptions if any
        if exceptions:
            for exception in exceptions:
                raise exception
        
        # Terminate pool
        pool.terminate()

        # Return results
        return pd.concat(results, ignore_index=True)
