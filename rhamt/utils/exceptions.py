"""Provides custom exceptions for the ``cfme`` module. """


class RHAMTException(Exception):
    """Base class for exceptions in the CFME tree

    Used to easily catch errors of our own making, versus errors from external libraries.

    """

    pass


class ItemNotFound(RHAMTException):
    """Raised when an item is not found in general."""
