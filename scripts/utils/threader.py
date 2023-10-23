import multiprocessing
import traceback
import logging

from . import logger
from multiprocessing.pool import ThreadPool as Pool

class LogExceptions(object):

    """
    Error logger for multiprocessing apply_async functions
    """

    def __init__(self, callable):
        self.__callable = callable

    def __call__(self, *args, **kwargs):
        try:
            result = self.__callable(*args, **kwargs)
        except Exception as e:
            # Here we add some debugging help. If multiprocessing's
            # debugging is on, it will arrange to log the traceback
            logger.LoggerBuilder.build(
                log_level=logging.ERROR
            ).error(traceback.format_exc())
            LogExceptions.error(e)
            # Re-raise the original exception so the Pool worker can
            # clean up
            raise

        # It was fine, give a normal answer
        return result

    @staticmethod
    def error(msg, *args):
        return multiprocessing.get_logger().error(msg, *args)


class LoggingPool(Pool):
    """
    Wrapper pool around logging exceptions
    """

    def apply_async(self, func, args=(), kwds={}, callback=None):
        return Pool.apply_async(self, LogExceptions(func), args, kwds, callback)