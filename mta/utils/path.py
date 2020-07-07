"""Project path helpers

Contains `pathlib.Path` objects for accessing common project locations.

Paths rendered below will be different in your local environment.
"""
import os
from distutils.sysconfig import get_python_lib as _get_python_lib
from pathlib import Path

import mta as _mta

PROJECT_PATH = Path(_mta.__file__).parent


def _is_site_installed(module):
    sitedir = _get_python_lib()
    return os.path.commonpath([module.__file__, sitedir]) == sitedir


MTA_EDITABLE_INSTALLED = not _is_site_installed(_mta)

# All configurations for MTA
CONF_PATH = PROJECT_PATH / "conf"

# log path for MTA
LOG_PATH = PROJECT_PATH / "log"
