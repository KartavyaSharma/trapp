"""
Error classes for the project.
"""

class NotAuthenticatedError(Exception):
    """
    Error raised when a user is not authenticated. Or no auth configuration exists.
    """
    pass