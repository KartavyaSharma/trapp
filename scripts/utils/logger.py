import constants
import logging


class LoggerBuilder:
    """
    Builder for logger objects
    """

    @staticmethod
    def build(logfile: str = None, log_level: any = None) -> logging.Logger:
        """
        Build logger with default configuration
        """
        filename = logfile.split("/")[-1] if logfile else constants.LOG_FILENAME.split("/")[-1]
        new_logger = logging.getLogger(f"trapp-{filename}")
        new_logger.setLevel(log_level or logging.INFO)

        new_logger_file_handler = logging.FileHandler(logfile or constants.LOG_FILENAME)
        new_logger_file_handler.setLevel(log_level or logging.INFO)
        new_logger_file_handler.setFormatter(logging.Formatter(constants.LOG_FORMAT, constants.LOG_DATEFMT))

        new_logger.addHandler(new_logger_file_handler)
        return new_logger
