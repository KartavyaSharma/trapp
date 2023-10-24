import pathlib
import sys

# Make the platform module available to the script
sys.path.append(f"{pathlib.Path(__file__).parent.resolve()}/../..")

from scripts.models.platform import Platform

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

    def non_headed_auth_inst(self):
        print("Please authenticate linkedin account manually.")