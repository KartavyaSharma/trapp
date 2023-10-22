"""
Error classes for the project.
"""

class NotAuthenticatedError(Exception):
    """
    Error raised when a user is not authenticated. Or no auth configuration exists.
    """
    pass

class InvalidURLError(Exception):
    """
    Error raised when a URL is invalid.
    """
    pass

class NoDriverSetError(Exception):
    """
    Error raised when no driver is set in a platform.
    """
    pass