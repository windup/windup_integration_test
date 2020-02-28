import warnings

import attr
import yaycl


class Configuration(object):
    """
    holds the current configuration
    """

    def __init__(self):
        self.yaycl_config = None

    def configure(self, config_dir, crypt_key_file=None):
        assert self.yaycl_config is None
        self.yaycl_config = yaycl.Config(config_dir=config_dir)

    def get_config(self, name):
        """returns a yaycl config object

        :param name: name of the configuration object
        """

        if self.yaycl_config is None:
            raise RuntimeError("cfme configuration was not initialized")
        return getattr(self.yaycl_config, name)


@attr.s(eq=False)
class DeprecatedConfigWrapper(object):
    """
    a wrapper that provides the old :code:``utils.conf`` api
    """

    configuration = attr.ib()
    _warn = attr.ib(default=False)

    def __getattr__(self, key):
        if self._warn:
            warnings.warn(
                "the configuration module {} will be deprecated".format(key),
                category=DeprecationWarning,
                stacklevel=2,
            )
        return self.configuration.get_config(key)

    @property
    def runtime(self):
        return self.configuration.runtime

    def __getitem__(self, key):
        if self._warn:
            warnings.warn(
                "the configuration module {} will be deprecated".format(key),
                category=DeprecationWarning,
                stacklevel=2,
            )
        return self.configuration.get_config(key)

    def __delitem__(self, key):
        # used in bad logging
        if self._warn:
            warnings.warn("clearing configuration is bad", stacklevel=2)

        del self.configuration.yaycl_config[key]


# for the initial usage we keep a global object
# later on we want to replace it
global_configuration = Configuration()
