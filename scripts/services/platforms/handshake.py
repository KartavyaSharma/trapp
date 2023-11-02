import constants
import pathlib
import sys
import time
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
)

# Make the platform module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.models.platform import Platform
from scripts.utils.errors import UnexpectedPageStateError
from scripts.utils.helpers import get_class_from_tag


class Handshake(Platform):
    name = "Handshake"
    base_url = "https://app.joinhandshake.com"
    login_url = "https://app.joinhandshake.com/login"

    def __init__(self, url: str):
        super().__init__(url)

    def login(self):
        wait = WebDriverWait(self.curr_driver, 120)
        wait.until(
            presence_of_element_located(
                # account dropdown button
                (By.ID, "account-dropdown")
            )
        )
        time.sleep(constants.SELENIUM_TIMEOUT)
        # Make sure title of current page contains "Feed"
        assert "Handshake" in self.curr_driver.title, UnexpectedPageStateError(
            self.curr_driver.url
        )

    def scrape(self) -> tuple[str, str, str, str]:
        inner_html = self.curr_driver.execute_script(
            'return document.getElementById("skip-to-content").innerHTML'
        )
        # Define BeautifulSoup object
        soup = BeautifulSoup(inner_html, "html.parser")
        # Define job post title pattern
        title_pattern = re.compile(r'class="style__job-title___[a-zA-Z0-9]{5}"')
        title_tags = soup.find_all(
            class_=get_class_from_tag(title_pattern.findall(inner_html)[0])
        )
        title = title_tags[0].get_text()
        # Define company name pattern
        company_pattern = re.compile(r'class="style__employer-name___[a-zA-Z0-9]{5}"')
        company_tags = soup.find_all(
            class_=get_class_from_tag(company_pattern.findall(inner_html)[0])
        )
        company = company_tags[0].get_text()
        # Define location pattern
        location_pattern = re.compile(
            r'class="style__list-with-tooltip___[a-zA-Z0-9]{5}"'
        )
        location_tags = soup.find_all(
            class_=get_class_from_tag(location_pattern.findall(inner_html)[0])
        )
        location = location_tags[0].get_text()
        return (title, company, location, self.url)

    def clean_url(self):
        self.url = self.url.split("?")[0]

    def save_cookies(self, cookies: any):
        """
        Save Selenium auth state for handshake to disk
        """
        cookie_objects = []
        for cookie in cookies:
            if cookie["name"] and cookie["domain"] == ".joinhandshake.com":
                cookie_objects.append(
                    {
                        "name": cookie["name"],
                        "value": cookie["value"],
                        "domain": cookie["domain"],
                    }
                )
        return cookie_objects

    def non_headed_auth_instruction(self):
        print("Please authenticate handshake account manually.")
