class MTAException(Exception):
    """Base class for MTA exceptions

    Used to easily catch errors of our own making, versus errors from external libraries.
    """

    pass


class ProjectNotFound(MTAException):
    """MTA Project not found"""

    pass


class ItemNotFound(MTAException):
    """Raised when an item is not found in general."""

    pass
