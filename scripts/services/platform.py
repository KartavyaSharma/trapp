import abc
import constants.constants as constants
import pickle
import time

from scripts.utils.errors import NoDriverSetError, InvalidURLError
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located


class Platform:

    __metaclass__ = abc.ABCMeta

    def __init__(self, url: str):
        self.url = url
        self.driver = None

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
    def login(self, email: str = None, password: str = None):
        """
        Selenium <platform> login workflow
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def scrape_job(self):
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
    def save_cookies(self):
        """
        Save Selenium auth state for <platform> to disk
        """
        raise NotImplementedError

    def set_driver(self, driver):
        """
        Set driver for platform
        """
        self.driver = driver

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

    def persist_auth_state(self):
        """
        Persist Selenium auth state to disk
        """
        pass

    def go_to_base_url(self):
        """
        Go to base URL
        """
        self.driver.get(self.base_url)

    def go_to_login_url(self):
        """
        Go to login URL
        """
        self.driver.get(self.login_url)

    def go_to_url(self):
        """
        Go to URL
        """
        self.driver.get(self.url)

    def load_cookies(self):
        print("Restoring auth state...")
        cookies = pickle.load(open(constants.CHROME_DRIVER_COOKIE_FILE, "rb"))
        self.driver.add_cookie(cookies)

    def init_scrape(self):
        """
        Setup scrape
        """
        # Load cookies
        self.go_to_base_url()
        time.sleep(2)
        self.load_cookies()  # Load cookies
        self.clean_url()
        self.go_to_url()
        time.sleep(3)


class LinkenIn(Platform):
    name = "LinkedIn"
    base_url = "https://www.linkedin.com"
    login_url = "https://www.linkedin.com/login"

    def __init__(self, url: str):
        super().__init__(url)

    def login(self):
        self.go_to_login_url()
        wait = WebDriverWait(self.driver, 30)
        wait.until(
            presence_of_element_located(
                # the `My Network` button
                (By.CSS_SELECTOR, ".global-nav__primary-item:nth-child(2) path")
            )
        )
        self.save_cookies()  # Save cookies

    def scrape_job(self) -> tuple[str, str, str]:
        self.init_scrape() # Assumes we are at job entry URL
        # Get job post title
        title = self.driver.find_element(By.CSS_SELECTOR, ".t-24").text
        post_info = self.driver.find_element(
            By.CSS_SELECTOR,
            # Returns <company name> · <location> <date posted> · <# of applicants>
            ".job-details-jobs-unified-top-card__primary-description > div" 
        ).text
        company = post_info.split("·")[0].strip()
        location = post_info.split("·")[1].split("  ")[0].strip()
        return (title, company, location)

    def clean_url(self):
        if "jobs" not in self.url or "view" not in self.url:
            if "=" not in self.url:
                raise InvalidURLError(self.url)
            job_id = self.url.split("=", 1)[1]
            self.url = self.base_url + f"/jobs/view/{job_id}/"

    def save_cookies(self):
        """
        Save Selenium auth state for LinkedIn to disk
        """
        print("Saving auth state...")
        time.sleep(10)
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            if (cookie['name'] == 'li_at'):
                cookie['domain'] = '.linkedin.com'
                x = {
                    'name': 'li_at',
                    'value': cookie['value'],
                    'domain': '.linkedin.com'
                }
                break
        pickle.dump(x, open(constants.CHROME_DRIVER_COOKIE_FILE, "wb"))
        print('Auth state saved!')


class Handshake(Platform):
    name = "Handshake"
    base_url = "https://app.joinhandshake.com"
    login_url = "https://app.joinhandshake.com/login"

    def __init__(self, url: str):
        super().__init__(url)

    def login(self):
        pass

    def scrape_job(self):
        pass


class PlatformBuilder:
    """
    Build platform instances
    """

    platforms = {
        "LinkedIn".lower(): LinkenIn,
        "Handshake".lower(): Handshake
    }

    @staticmethod
    def build(platform_name: str, url: str) -> Platform:
        """
        Build platform instance from URL
        """
        platform_name = platform_name.lower()
        try:
            return PlatformBuilder.platforms[platform_name](url)
        except KeyError:
            raise NotImplementedError
