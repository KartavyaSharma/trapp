import abc


class Platform:

    __metaclass__ = abc.ABCMeta

    @property
    def base_url(self):
        raise NotImplementedError

    @property
    def login_url(self):
        raise NotImplementedError

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


class LinkenIn(Platform):
    base_url = "https://www.linkedin.com/"
    login_url = "https://www.linkedin.com/login"

    def login(self):
        pass

    def scrape_job(self):
        pass


class Handshake(Platform):
    base_url = "https://app.joinhandshake.com/"
    login_url = "https://app.joinhandshake.com/login"

    def login(self):
        pass

    def scrape_job(self):
        pass
