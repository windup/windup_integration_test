"""Project path helpers

Contains `pathlib.Path` objects for accessing common project locations.

Paths rendered below will be different in your local environment.
"""
import os
from distutils.sysconfig import get_python_lib as _get_python_lib
from pathlib import Path

import rhamt as _rhamt

PROJECT_PATH = Path(_rhamt.__file__).parent


def _is_site_installed(module):
    sitedir = _get_python_lib()
    return os.path.commonpath([module.__file__, sitedir]) == sitedir


RHAMT_EDITABLE_INSTALLED = not _is_site_installed(_rhamt)

# All configurations for RHAMT
CONF_PATH = PROJECT_PATH / "conf"

# log path for RHAMT
LOG_PATH = PROJECT_PATH / "log"
