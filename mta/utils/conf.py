import sys

from mta.utils.config import DeprecatedConfigWrapper
from mta.utils.config import global_configuration
from mta.utils.path import CONF_PATH
from mta.utils.path import YAML_PATH

global_configuration.configure(
    config_dir=CONF_PATH,
    crypt_key_file=YAML_PATH,
)

# sys.modules[__name__] = global_configuration
sys.modules[__name__] = DeprecatedConfigWrapper(global_configuration)