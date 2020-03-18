import logging

from rhamt.utils.path import LOG_PATH

"""
Example Usage
^^^^^^^^^^^^^

.. code-block:: python

    from rhamt.utils.log import logger

    logger.debug('debug log message')
    logger.info('info log message')
    logger.warning('warning log message')
    logger.error('error log message')
    logger.critical('critical log message')
"""

# logger
logger = logging.getLogger("rhamt")

# stream Handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)
stream_handler.setFormatter(logging.Formatter("%(levelname)s : %(message)s"))

# File Handler
LOG_PATH.mkdir(exist_ok=True)
rhamt_log_file = LOG_PATH / "rhamt.log"
file_handler = logging.FileHandler(rhamt_log_file, mode="a")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(levelname)s : %(asctime)s - %(message)s"))

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addFilter(stream_handler)
