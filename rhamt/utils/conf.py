import sys

from rhamt.utils.config import global_configuration
from rhamt.utils.path import CONF_PATH

global_configuration.configure(config_dir=CONF_PATH)

sys.modules[__name__] = global_configuration
