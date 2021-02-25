import pytest

from mta.base.application.implementations.operator_ui import navigate_to as op_nav
from mta.base.application.implementations.operator_ui import ViaOperatorUI
from mta.base.application.implementations.web_ui import navigate_to as web_nav
from mta.base.application.implementations.web_ui import ViaWebUI


@pytest.mark.smoke
@pytest.mark.parametrize("context", [ViaOperatorUI, ViaWebUI])
def test_login(application, context):
    """Test login nav destination"""
    with application.context.use(context):
        nav_to = op_nav if context is ViaOperatorUI else web_nav
        view = nav_to(application.collections.base, "LoggedIn")
        assert view.is_displayed
