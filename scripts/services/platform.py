import abc

from scripts.utils.errors import NoDriverSetError

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

    # @property
    # def driver(self):
    #     self.driver = None # Default driver value

    @property
    def job_entry_url(self):
        self.jobs_url = self.base_url + "jobs" # Might not exist, default value

    @abc.abstractclassmethod
    def login(self):
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

    def set_driver(self, driver):
        """
        Set driver for platform
        """
        self.driver = driver

    # @driver.setter
    # def driver(self, driver):
    #     """
    #     Set driver for platform
    #     """
    #     self.driver = driver

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


class LinkenIn(Platform):
    name = "LinkedIn"
    base_url = "https://www.linkedin.com/"
    login_url = "https://www.linkedin.com/login"

    def __init__(self, url: str):
        super().__init__(url)

    def login(self):
        pass

    def scrape_job(self):
        pass


class Handshake(Platform):
    name = "Handshake"
    base_url = "https://app.joinhandshake.com/"
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
