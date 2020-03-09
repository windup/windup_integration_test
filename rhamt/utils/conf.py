import sys

from rhamt.utils import path
from rhamt.utils.config import global_configuration

global_configuration.configure(config_dir=path.CONF_PATH)

sys.modules[__name__] = global_configuration
