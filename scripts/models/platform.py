import abc
import constants.constants as constants
import pickle
import time

from scripts.utils.errors import NoDriverSetError


class Platform:
    """
    Abstract base class for platform implementations
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, url: str):
        self.url = url
        self.driver = None
        self.auth_driver = None
        self.curr_driver = None

    @property
    def name(self):
        raise NotImplementedError

    @property
    def base_url(self):
        raise NotImplementedError

    @property
    def login_url(self):
        raise NotImplementedError

    @property
    def job_entry_url(self):
        self.jobs_url = self.base_url + "jobs"  # Might not exist, default value

    @abc.abstractclassmethod
    def login(self, headed: bool = True):
        """
        Selenium <platform> login workflow
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def scrape(self):
        """
        Selenium <platform> scrape job workflow
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def clean_url(self):
        """
        Clean URL for <platform>
        """
        raise NotImplementedError

    @abc.abstractmethod
    def save_cookies(self, cookies: any):
        """
        Save Selenium auth state for <platform> to disk
        """
        raise NotImplementedError

    def set_driver(self, driver):
        """
        Set driver for platform
        """
        self.driver = driver

    def set_auth_driver(self, driver):
        """
        Set authentication driver for platform
        """
        self.auth_driver = driver

    def set_curr_driver(self, driver):
        """
        Set current driver for platform
        """
        self.curr_driver = driver

    def init(self):
        """
        Selenium init workflow
        """
        # Make sure driver is set
        if not self.driver:
            raise NoDriverSetError

    def cold_start(self):
        """
        Selenium cold start (unauthenticated) workflow
        """
        self.login()
        self.scrape_job()

    def go_to_base_url(self):
        """
        Go to base URL
        """
        self.curr_driver.get(self.base_url)

    def go_to_login_url(self):
        """
        Go to login URL
        """
        self.curr_driver.get(self.login_url)

    def go_to_url(self):
        """
        Go to URL
        """
        self.curr_driver.get(self.url)

    def load_cookies(self):
        print("Restoring auth state...")
        cookies = pickle.load(open(self.get_cookie_file(), "rb"))
        self.curr_driver.add_cookie(cookies)

    def init_scrape(self):
        """
        Setup scrape
        """
        self.init()  # Init platform
        self.set_curr_driver(self.driver)  # Set current driver as main driver
        # Load cookies
        self.go_to_base_url()
        time.sleep(constants.SELENIUM_TIMEOUT)
        self.load_cookies()  # Load cookies
        self.clean_url()
        self.go_to_url()
        time.sleep(constants.SELENIUM_TIMEOUT)

    def get_cookie_file(self):
        """
        Get cookie file path
        """
        return constants.CHROME_DRIVER_COOKIE_FILE.split("<platform>")[0] + self.name.lower() + ".pkl"

    def clean(self):
        """
        Kill current driver
        """
        self.curr_driver.close()
    
    def retrieve_auth_state(self):
        """
        Gets cookies and saves them to disk
        """
        print("Saving auth state...")
        cookies = self.curr_driver.get_cookies()
        cookies_to_save = self.save_cookies(cookies=cookies)
        pickle.dump(cookies_to_save, open(self.get_cookie_file(), "wb"))
        print('Auth state saved!')

    def non_headed_auth_instruction(self):
        """
        Instructions for authenticating <platform> on non-headed systems
        """
        raise NotImplementedError
