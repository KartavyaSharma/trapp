"""
Error classes for the project.
"""


class NotAuthenticatedError(Exception):
    """
    Error raised when a user is not authenticated. Or no auth configuration exists.
    """

    msg = "Forbidden: not authenticated"

    def __init__(self, *args: object) -> None:
        super().__init__(self.msg)


class InvalidURLError(Exception):
    """
    Error raised when a URL is invalid.
    """

    def __init__(self, msg) -> None:
        self.url = msg
        self.msg = f"Invalid URL found! No matching platform.\n\tURL: {msg}"
        super().__init__(self.msg)


class NoDriverSetError(Exception):
    """
    Error raised when no driver is set in a platform.
    """

    msg = "No driver set on selected platform."

    def __init__(self, *args: object) -> None:
        super().__init__(self.msg)


class NoHeadedSupportError(Exception):
    """
    Error raised when a platform does not support headed mode.
    """

    msg = "No headed support for selected platform."

    def __init__(self, msg) -> None:
        self.msg = f"NoHeadedSupportError: {msg}"
        super().__init__(self.msg)


class UnexpectedPageStateError(Exception):
    """
    Error raised when the scraper encounters an unexpected page state.
    """

    def __init__(self, msg) -> None:
        self.msg = f"Unexpected page state encountered for {msg}"
        super().__init__(self.msg)


class ServiceAlreadyRunningError(Exception):
    """
    Error raised when a service is already running.
    """

    def __init__(self, msg) -> None:
        self.msg = f"Service already running: {msg}"
        super().__init__(self.msg)


class ServiceNotRunningError(Exception):
    """
    Error raised when a service is not running.
    """

    def __init__(self, msg) -> None:
        self.msg = f"Service not running: {msg}"
        super().__init__(self.msg)


class AutoServiceError(Exception):
    """
    Wrapper class for errors raised by auto service
    """

    def __init__(self, msg, err, url) -> None:
        self.msg = f"{msg}: {err}"
        self.url = url
        super().__init__(self.msg)


class PoolException(Exception):
    """
    Wrapper around exceptions raised by thread pool
    """

    def __init__(self, err) -> None:
        self.err = err
        super().__init__()


def get_error_types() -> any:
    """
    Get error types from errors module

    @return: Error types
    """
    import sys
    import inspect

    return inspect.getmembers(sys.modules[__name__], inspect.isclass)
