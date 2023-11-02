import os
import pathlib

import constants

from ..models import platform
from scripts.utils.errors import *


class VaultService:
    def __init__(self):
        pass

    def configure(self):
        pass

    def unlock(self):
        pass

    def loadIntoMemory(self):
        pass

    @staticmethod
    def isAuthenticated(
        platform: platform.Platform, headed_support: bool = True
    ) -> bool:
        """
        Check if user has saved auth state for platform
        """
        if platform.login_url == "":
            return True
        platform_dir_path = pathlib.Path(
            constants.CHROME_DRIVER_COOKIE_DIR.replace(
                "<platform>", platform.name.lower()
            )
        )
        if not platform_dir_path.exists():
            if not headed_support:
                platform.non_headed_auth_instruction()
                raise NoHeadedSupportError(platform.name)
            return False
        return True

    @staticmethod
    def authenticate(platform: platform.Platform, auth_engine: any = None) -> None:
        if not auth_engine:
            raise NotImplementedError
        auth_engine.create_driver()
        platform.set_auth_driver(auth_engine.driver)
        platform.login_wrapper()

    @staticmethod
    def isPresent() -> bool:
        """
        Check if Vault is present on the system
        """
        return os.path.exists(constants.VAULT_PATH)
