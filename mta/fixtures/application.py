import attr
import pytest

from mta.base.application import Application
from mta.utils import conf

PLUGIN_KEY = "app-holder"


@attr.s(cmp=False, hash=False)
class ApplicationHolderPlugin(object):
    primary_application = attr.ib()

    def pytest_sessionfinish(self):
        """close browser after test finished"""
        self.primary_application.web_ui.browser_manager.close()

    @pytest.fixture(scope="session")
    def application(self):
        """Returns an instance of the application object"""
        return self.primary_application

    @pytest.fixture(scope="session")
    def app(self, application):
        """Returns an instance of the application object"""
        return application


@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """Hook to get app and conf"""
    config._mta_conf = conf
    app = Application(config=conf.get_config("env"))
    plugin = ApplicationHolderPlugin(app)
    config.pluginmanager.register(plugin)
