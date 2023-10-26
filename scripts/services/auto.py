import constants
import datetime
import multiprocessing
import pandas as pd
import pathlib
import threading
import sys

from . import configuration, scraper, redis
from scripts.models import entry, status

# Added to make the utils module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.utils.errors import ServiceAlreadyRunningError, AutoServiceError, InvalidURLError
from scripts.utils.helpers import has_gui, verify_headless_support 
from scripts.utils.threader import LoggingPool
from scripts.utils.logger import LoggerBuilder

class AutoService(object):
    """
    Service for automatically generating job entries in
    the source CSV file from a url
    """

    def __init__(self):
        self.verify_gui_support() # Run GUI support check
        self.setup() # Initialize service instance variables
        self.start_redis() # Start Redis service

    def __getattribute__(self, __name: str) -> any:
        if __name != "thread_local":
            return super().__getattribute__(__name)
    
    def __del__(self):
        self.teardown() # Stop running processes and services
    
    def setup(self) -> None:
        """
        Setup service instance and start Redis service
        """
        # Define threading
        self.thread_local = threading.local() 
        # Define builders
        self.configuration_builder = configuration.ConfigurationBuilder()
        self.scraper_builder = scraper.ScraperBuilder()
        self.logger_builder = LoggerBuilder()
        # Partially build the auth engine
        self.auth_engine = self.scraper_builder.build(
            opts=constants.CHROME_DRIVER_NO_HEADLESS_OPTS, # Run in non-headless mode 
            delay_driver_build=True,
            headed_support=self.gui_support
        )
    
    def verify_gui_support(self) -> None:
        """
        Check if GUI is supported
        """
        self.gui_support = has_gui()
        if not self.gui_support:
            # Start virtual display
            print(f"{constants.WARNING}GUI support not detected, running in headless mode...{constants.ENDC}")
            verify_headless_support()
            ####### DO NOT REMOVE CONDITIONAL IMPORT #######
            from pyvirtualdisplay import Display # Should be installed in verify_headless_support()
            ################################################
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()

    def start_redis(self) -> None:
        """
        Start Redis service
        """
        print("Starting Redis service...", end=' ')
        self.service = redis.RedisService(password="redis")
        try:
            self.service.init()
        except ServiceAlreadyRunningError as e:
            print(e)
        assert self.service.status(), "Redis service not running"
        print(f"{constants.OKGREEN}OK{constants.ENDC}")
    
    def teardown(self) -> None:
        """
        Stop running processes and services
        """
        # If GUI is not supported, stop virtual display
        if not self.gui_support:
            self.display.stop()
        # Stop Redis service
        print("Stopping Redis service...", end=' ')
        self.service.stop()
        print(f"{constants.OKGREEN}OK{constants.ENDC}")
        # Delete thread local
        del self.thread_local

    def run(self, url: str) -> pd.DataFrame:
        """
        @param url: URL to scrape job application data from
        @param result_queue: Queue to store multiprocessing results in (optional)
        @return: Pandas DataFrame containing a single row job entry 
        """
        # Define builders
        # Create configuration and scraper engine
        config = self.configuration_builder.build(url)
        scraper_engine = self.scraper_builder.build()
        try:
            # Run scraper
            (title, company, location, post_url) = scraper_engine.run(config, auth_engine=self.auth_engine)
        except Exception as e:
            raise AutoServiceError(msg=f"Error encountered while scraping {url}", err=e, url=url)
        
        # Create entry
        new_entry = entry.Entry(
            company=company,
            position=title,
            date_applied=datetime.datetime.now(),
            status=status.Status.INIT,
            link=post_url,
            notes=f"Addtional Information:{location}"
        )

        # Get dataframe
        return new_entry.create_dataframe()


    def batch_run(self, urls: list[str]) -> pd.DataFrame:
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
        failed_urls = []
        # Start worker functions
        for url in urls:
            results.append(pool.apply_async(self.run, args=(url,)))

        # Wait for all workers to finish
        pool.close()
        pool.join()

        for result in results:
            try:
                r = result.get()
            except Exception as e:
                if isinstance(e, AutoServiceError) or isinstance(e, InvalidURLError):
                    if isinstance(e, InvalidURLError):
                        print(f"[{constants.FAIL}ERROR{constants.ENDC}]: Invalid URL found! No matching platform. URL: {e.msg.split(': ')[1]}")
                    else:
                        failed_urls.append(e.url)
                else:
                    print(f"{constants.FAIL}Unknown error encountered! Check logs at {constants.LOG_FILENAME.replace(constants.PROJECT_ROOT, '')}{constants.ENDC}")
                continue
            if not isinstance(r, Exception):
                final.append(r)

        if failed_urls:
            print(f"[{constants.INFOBLUE}INFO{constants.ENDC}]: {constants.WARNING}{len(failed_urls)} job(s) failed! Check logs at {constants.LOG_FILENAME.replace(constants.PROJECT_ROOT, '')}{constants.ENDC}")
            for url in failed_urls:
                print(f"[{constants.FAIL}ERROR{constants.ENDC}]: {url}")

        # Terminate pool
        pool.terminate()

        # Return results
        if not final:
            print(f"{constants.WARNING}No usable results found!{constants.ENDC}")
            return pd.DataFrame()
        return pd.concat(final, ignore_index=True), failed_urls
    
