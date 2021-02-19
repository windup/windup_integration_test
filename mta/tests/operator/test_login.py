import pytest

from mta.base.application.implementations.operator_ui import ViaOperatorWebUI
from mta.base.application.implementations.web_ui import navigate_to


@pytest.mark.smoke
# @pytest.mark.web_console
@pytest.mark.parametrize('context', [ViaOperatorWebUI])
def test_login(application):
    """Test login nav destination"""
    view = navigate_to(application.collections.base, "LoggedIn")
    assert view.is_displayed