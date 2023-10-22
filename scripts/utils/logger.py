import logging

import constants.constants as constants

class LoggerBuilder:
    """
    Builder for logger objects
    """

    @staticmethod
    def build() -> logging:
        """
        Build logger with default configuration
        """
        logging.basicConfig(
            filename=constants.LOG_FILENAME,
            filemode=constants.LOG_FILEMODE,
            format=constants.LOG_FORMAT,
            datefmt=constants.LOG_DATEFMT
        )
        return logging
