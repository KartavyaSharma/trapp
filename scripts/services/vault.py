import os

import constants.constants as constants

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
    def authenticate():
        if not Vault.isPresent():
            raise NotAuthenticatedError
        else:
            pass

    @staticmethod
    def isPresent() -> bool:
        """
        Check if Vault is present on the system
        """
        return os.path.exists(constants.VAULT_PATH)


def main():
    pass
