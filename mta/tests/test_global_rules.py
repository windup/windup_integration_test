from mta.base.application.implementations.web_ui import navigate_to


def test_crud_global_custom_rule(application):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Login to MTA web console
            2. Navigate to Global > Rules configuration > Custom rules
            3. Click on Add rule button and browse rules file
            4. Click on Close button
        expectedResults:
            1. Custom rules file should be listed in table
    """
    file_name = "custom.Test1rules.rhamt.xml"
    view = navigate_to(application.collections.globalconfigurations, "Custom")
    view.custom_rules.upload_rule_file(file_name)
    view.table.wait_displayed("20s")
    assert file_name in [rules["Short path"] for rules in view.table.read()]
    assert view.custom_rules.delete(file_name)


def test_search_global_custom_rule(application, request):
    """ Test to search global custom rules file from table

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Login to MTA web console
            2. Navigate to Global > Rules configuration > Custom rules
            3. Click on Add rule button and browse rules files
            4. Click on Close button
            5. Add value in 'Filter by short path' input box and hit enter
        expectedResults:
            1. Custom rules file should searched by substring
    """
    file_name = "custom.Test1rules.rhamt.xml"
    view = navigate_to(application.collections.globalconfigurations, "Custom")
    view.custom_rules.upload_rule_file(file_name)
    view.table.wait_displayed("20s")
    view.search.fill("rhamt")

    @request.addfinalizer
    def _finalize():
        view.search.fill("")
        view.custom_rules.delete(file_name)

    assert file_name in [rules["Short path"] for rules in view.table.read()]
    view.search.fill("rhamt-invalid")
    try:
        assert file_name not in [rules["Short path"] for rules in view.table.read()]
    except IndexError:
        pass
