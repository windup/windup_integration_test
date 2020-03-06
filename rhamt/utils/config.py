import yaycl


class Configuration(object):
    """ holds the current configuration"""

    def __init__(self):
        self.yaycl_config = None

    def configure(self, config_dir):
        assert self.yaycl_config is None
        self.yaycl_config = yaycl.Config(config_dir=config_dir)

    def get_config(self, name):
        """returns a yaycl config object

        :param name: name of the configuration object
        """

        if self.yaycl_config is None:
            raise RuntimeError("RHAMT configuration was not initialized")
        return getattr(self.yaycl_config, name)


# for the initial usage we keep a global object
# later on we want to replace it
global_configuration = Configuration()
