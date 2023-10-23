import os
import pathlib

import constants.constants as constants

from . import platform
from scripts.utils.errors import *

class Vault:

    def __init__(self):
        pass

    def configure(self):
        pass

    def unlock(self):
        pass

    def loadIntoMemory(self):
        pass

    @staticmethod
    def isAuthenticated(platform: platform.Platform, headed_support:bool = True) -> bool:
        """
        Check if user has saved auth state for platform
        """
        file_path = pathlib.Path(constants.CHROME_DRIVER_COOKIE_FILE.replace("<platform>", platform.name.lower()))
        if not file_path.exists():
            if not headed_support:
                platform.non_headed_auth_inst()
                raise NoHeadedSupportError(platform.name)
            return False
        return True

    @staticmethod
    def authenticate(platform: platform.Platform, auth_engine: any = None) -> None:
        if not auth_engine:
            raise NotImplementedError
        auth_engine.create_driver()
        platform.set_auth_driver(auth_engine.driver)
        platform.login(headed=auth_engine.headed_support)

    @staticmethod
    def isPresent() -> bool:
        """
        Check if Vault is present on the system
        """
        return os.path.exists(constants.VAULT_PATH)


def main():
    pass
