import abc
import constants
import pickle
import time

from pathlib import Path
from scripts.utils.errors import NoDriverSetError, AutoServiceError


class Platform:
    """
    Abstract base class for platform implementations
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, url: str):
        self.url = url
        self.clean_url()
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

    def login_wrapper(self):
        """
        Wrapper for login workflow
        """
        if self.login_url:
            # Set current driver as auth driver
            self.set_curr_driver(self.auth_driver)
            self.go_to_login_url()
            self.login()  # Login
            self.retrieve_auth_state()
            self.clean()
            self.set_curr_driver(self.driver)  # Set current driver as main driver

    def scrape_wrapper(self):
        """
        Setup scrape
        """
        self.init()  # Init platform
        self.set_curr_driver(self.driver)  # Set current driver as main driver
        # Load cookies
        self.go_to_base_url()
        time.sleep(constants.SELENIUM_TIMEOUT)
        self.load_cookies()  # Load cookies
        self.go_to_url()
        time.sleep(constants.SELENIUM_TIMEOUT)
        try:
            res = self.scrape()  # Scrape
        except Exception as e:
            self.clean()
            raise AutoServiceError(f"Scraping {self.url} failed", e, self.url)
        self.clean()
        return res

    def retrieve_auth_state(self):
        """
        Gets cookies and saves them to disk
        """
        print("Saving auth state...", end=" ")
        if not Path(
            constants.CHROME_DRIVER_COOKIE_DIR.replace("<platform>", self.name.lower())
        ).exists():
            Path(
                constants.CHROME_DRIVER_COOKIE_DIR.replace(
                    "<platform>", self.name.lower()
                )
            ).mkdir(parents=True, exist_ok=True)
        cookies = self.curr_driver.get_cookies()
        cookies_to_save = self.save_cookies(cookies=cookies)
        for cookie_object in cookies_to_save:
            pickle.dump(cookie_object, open(self.get_cookie_file(cookie_object), "wb"))
        print(f"{constants.OKGREEN}OK{constants.ENDC}")

    def load_cookies(self):
        for file in Path(
            constants.CHROME_DRIVER_COOKIE_DIR.replace("<platform>", self.name.lower())
        ).glob("*.pkl"):
            cookie_object = pickle.load(open(file, "rb"))
            self.curr_driver.add_cookie(cookie_object)

    def get_cookie_file(self, cookie_object: any = None):
        """
        Get cookie file path
        """
        file = (
            constants.CHROME_DRIVER_COOKIE_DIR.replace("<platform>", self.name.lower())
            + "/"
            + cookie_object["name"]
            + ".pkl"
        )
        return file

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

    def clean(self):
        """
        Kill current driver
        """
        self.curr_driver.close()

    def non_headed_auth_instruction(self):
        """
        Instructions for authenticating <platform> on non-headed systems
        """
        print("No authentication required for this platform.")
