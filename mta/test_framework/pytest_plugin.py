import logging

logger = logging.getLogger("mta.test_framework.pytest_plugin")

pytest_plugins = ["mta.fixtures.application", "mta.fixtures.project_fixture"]


def pytest_configure(config):
    config.addinivalue_line("markers", "web_console: MTA Web Console tests")
    config.addinivalue_line("markers", "cli: MTA cli tests")
    config.addinivalue_line("markers", "smoke: General smoke tests")
    config.addinivalue_line("markers", "ci: General smoke tests run on GitHub CI")
