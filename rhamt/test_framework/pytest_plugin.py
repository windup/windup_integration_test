import logging

logger = logging.getLogger("rhamt.test_framework.pytest_plugin")

pytest_plugins = ["rhamt.fixtures.application"]


def pytest_configure(config):
    config.addinivalue_line("markers", "web_console: RHAMT Web Console tests")
    config.addinivalue_line("markers", "cli: RHAMT cli tests")
    config.addinivalue_line("markers", "smoke: General smoke tests")
