import constants
import pathlib
import sys
import time

from scripts.utils.errors import InvalidURLError, UnexpectedPageStateError
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    presence_of_element_located,
    invisibility_of_element_located,
)
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

# Make the platform module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.models.platform import Platform


class LinkenIn(Platform):
    name = "LinkedIn"
    base_url = "https://www.linkedin.com"
    login_url = "https://www.linkedin.com/login"

    def __init__(self, url: str):
        super().__init__(url)

    def login(self):
        wait = WebDriverWait(self.curr_driver, 120)  # Wait for user to login
        wait.until(
            invisibility_of_element_located(
                # the `Forgot password?` link
                (By.LINK_TEXT, "Forgot password?")
            )
        )
        wait = WebDriverWait(self.curr_driver, constants.SELENIUM_TIMEOUT)
        try:
            if wait.until(
                presence_of_element_located(
                    # the `possible verify page`
                    (By.ID, "input__email_verification_pin")
                )
            ):
                print(
                    "Linkedin detected suspicious activity on your account. Please enter the verification code sent to your email."
                )
                verification_code = input("Enter verification code: ")
                self.curr_driver.find_element(
                    By.ID, "input__email_verification_pin"
                ).send_keys(verification_code)
                # Press enter to submit verification code
                self.curr_driver.find_element(
                    By.ID, "input__email_verification_pin"
                ).send_keys(Keys.ENTER)
        except TimeoutException:
            pass
        wait.until(
            presence_of_element_located(
                # the `My Network` button
                (By.CSS_SELECTOR, ".global-nav__primary-item:nth-child(2) path")
            )
        )
        time.sleep(constants.SELENIUM_TIMEOUT)
        # Make sure title of current page contains "Feed"
        assert "Feed" in self.curr_driver.title, UnexpectedPageStateError(
            self.curr_driver.url
        )

    def scrape(self) -> tuple[str, str, str, str]:
        # Get job post title
        title = self.curr_driver.find_element(By.CSS_SELECTOR, ".t-24").text
        post_info = self.curr_driver.find_element(
            By.CSS_SELECTOR,
            # Returns <company name> · <location> <date posted> · <# of applicants>
            # ".job-details-jobs-unified-top-card__primary-description > div",
            ".job-details-jobs-unified-top-card__primary-description-container",
        ).text
        company = post_info.split("·")[0].strip()
        location = post_info.split("·")[1].split("  ")[0].strip()
        return (title, company, location, self.url)

    def clean_url(self):
        if "jobs" not in self.url or "view" not in self.url:
            if "=" not in self.url:
                raise InvalidURLError(self.url)
            job_id = self.url.split("=", 1)[1]
            self.url = self.base_url + f"/jobs/view/{job_id}/"

    def save_cookies(self, cookies: any):
        """
        Save Selenium auth state for LinkedIn to disk
        """
        cookie_objects = []
        for cookie in cookies:
            if cookie["name"] == "li_at":
                cookie["domain"] = ".linkedin.com"
                cookie_objects.append(
                    {
                        "name": "li_at",
                        "value": cookie["value"],
                        "domain": ".linkedin.com",
                    }
                )
                break
        return cookie_objects

    def non_headed_auth_instruction(self):
        print("Please authenticate linkedin account manually.")
