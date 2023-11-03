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


class GreenHouse(Platform):
    name = "GreenHouse"
    base_url = "https://boards.greenhouse.io"
    login_url = ""

    def __init__(self, url: str):
        super().__init__(url)

    def login(self):
        pass

    def scrape(self) -> tuple[str, str, str, str]:
        wait = WebDriverWait(self.curr_driver, constants.SELENIUM_TIMEOUT)
        wait.until(
            presence_of_element_located(
                # account dropdown button
                (By.CLASS_NAME, "logo-container")
            )
        )
        title = self.curr_driver.find_element(By.CLASS_NAME, "app-title").text
        company = self.curr_driver.find_element(
            By.CLASS_NAME, "company-name"
        ).text.replace("at ", "")
        location = self.curr_driver.find_element(By.CLASS_NAME, "location").text
        return (title, company, location, self.url)

    def clean_url(self):
        pass

    def save_cookies(self, cookies: any):
        """
        Save Selenium auth state for LinkedIn to disk
        """
        cookie_objects = []
        return cookie_objects
