import pytest

from mta.base.application.implementations.web_ui import navigate_to


@pytest.mark.smoke
@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI"], indirect=True)
def test_login(mta_app):
    """Test login nav destination

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: smoke
        casecomponent: WebConsole
        testSteps:
            1. Login to MTA project
        expectedResults:
            1. It should successfully navigate to project all page or
               Welcome to the Migration Toolkit for Applications page
    """

    view = navigate_to(mta_app.collections.base, "LoggedIn")
    assert view.is_displayed
