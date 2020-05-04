class RHAMTException(Exception):
    """Base class for RHAMT exceptions

    Used to easily catch errors of our own making, versus errors from external libraries.
    """

    pass


class ProjectNotFound(RHAMTException):
    """RHAMT Project not found"""

    pass


class ItemNotFound(RHAMTException):
    """Raised when an item is not found in general."""

    pass
