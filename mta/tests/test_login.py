import pytest

from mta.base.application.implementations.web_ui import navigate_to


@pytest.mark.smoke
@pytest.mark.parametrize("mta_context", ["ViaWebUI", "ViaOperatorUI"])
def test_login(application, mta_context):
    """Test login nav destination"""
    application.mta_context = mta_context
    view = navigate_to(application.collections.base, "LoggedIn")
    assert view.is_displayed
