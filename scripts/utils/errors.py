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
        self.msg = f"Invalid URL found! No matching platform.\n\tURL: {msg}"
        super().__init__(self.msg)


class NoDriverSetError(Exception):
    """
    Error raised when no driver is set in a platform.
    """
    msg = "No driver set on selected platform."

    def __init__(self, *args: object) -> None:
        super().__init__(self.msg)


def get_error_types() -> any:
    """
    Get error types from errors module

    @return: Error types
    """
    import sys
    import inspect

    return inspect.getmembers(sys.modules[__name__], inspect.isclass)
