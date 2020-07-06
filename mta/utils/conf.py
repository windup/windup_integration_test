import sys

from mta.utils.config import global_configuration
from mta.utils.path import CONF_PATH

global_configuration.configure(config_dir=CONF_PATH)

sys.modules[__name__] = global_configuration
