import pytest

from mta.base.application.implementations.web_ui import navigate_to


@pytest.mark.smoke
@pytest.mark.web_console
@pytest.mark.parametrize("context", ["ViaOperatorUI"])
def test_login(application, context):
    """Test login nav destination"""
    if context == "ViaOperatorUI":
        view = navigate_to(application.collections.base, "OCPLoggedIn")
    else:
        view = navigate_to(application.collections.base, "LoggedIn")
    assert view.is_displayed
