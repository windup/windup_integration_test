import pytest

from mta.base.application.implementations.operator_ui import navigate_to
from mta.base.application.implementations.operator_ui import ViaOperatorUI

# from mta.base.application.implementations.web_ui import ViaWebUI

# from mta.base.application.implementations.web_ui import navigate_to


@pytest.mark.smoke
# @pytest.mark.web_console
@pytest.mark.parametrize("context", [ViaOperatorUI])
def test_login(application, context):
    """Test login nav destination"""
    with application.context.use(context):
        view = navigate_to(application.collections.base, "LoggedIn")
        assert view.is_displayed
