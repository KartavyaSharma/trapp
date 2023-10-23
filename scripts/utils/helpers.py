import multiprocessing
import os
import traceback
import logging
import re
import subprocess

from . import logger
from multiprocessing.pool import ThreadPool as Pool


def has_gui() -> bool:
    """
    Check if running on a GUI

    @return: True if running on a GUI, False otherwise
    """
    # If system uname -s is Darwin, then we are on macOS
    if os.uname().sysname == "Darwin":
        return True
    check_xorg = subprocess.check_output(
        ["type", "Xorg"],
        stderr=subprocess.DEVNULL,
        universal_newlines=True,
        shell=True
    )
    if check_xorg == "Xorg is /usr/bin/Xorg\n":
        return True
    # Check /usr/share/xsessions
    try:
        check_xsessions = subprocess.check_output(
            ["\ls /usr/share/xsessions"],
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            shell=True
        )
    except Exception as e:
        return False
    # if not "No such file or directory" in check_xsessions:
    #     return True
    check_dir = subprocess.check_output(
        ["\ls", "/usr/bin/*session"],
        stderr=subprocess.DEVNULL,
        universal_newlines=True,
        shell=True
    )
    # If check_dir has only /usr/bin/byobu-select-session  /usr/bin/dbus-run-session, then we are on a server
    if check_dir == "/usr/bin/byobu-select-session  /usr/bin/dbus-run-session\n":
        return False
    elif "No such file or directory" not in check_dir:
        return True
    return False
 

def get_root_from_url(url: str) -> str:
    """
    Get root domain from URL

    @param url: URL to extract root domain from
    @return: Root domain of URL
    """
    regex = r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+)"
    return re.findall(regex, url)[0]


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
                log_level=logging.ERROR).error(traceback.format_exc()
            )
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
