import fauxfactory
import pytest

from mta.base.application.implementations.web_ui import navigate_to
from mta.entities.analysis_results import AnalysisResults


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


@pytest.fixture
def add_global_custom_rule(application):
    """This fixture with upload global custom rule file"""
    file_name = "custom.Test1rules.rhamt.xml"
    view = navigate_to(application.collections.globalconfigurations, "Custom")
    view.custom_rules.upload_rule_file(file_name)
    view.table.wait_displayed("20s")
    return file_name


def test_analysis_global_custom_rule(application, request, add_global_custom_rule):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Upload global custom role file
            2. Create project and run analysis
            3. Go to analysis details page and check if custom rules contains global scope custom
               rule file
        expectedResults:
            1. Analysis should be completed successfully
    """
    file_name = add_global_custom_rule
    project = application.collections.projects.create(
        name=fauxfactory.gen_alphanumeric(12, start="project_"),
        description=fauxfactory.gen_alphanumeric(start="desc_"),
        app_list=["acmeair-webapp-1.0-SNAPSHOT.war"],
    )
    assert project.exists
    request.addfinalizer(project.delete_if_exists)
    analysis_results = AnalysisResults(application, project.name)
    view = navigate_to(analysis_results, "AnalysisDetailsPage")
    view.wait_displayed()
    card_info = view.custom_rules.read()
    assert f"Global scope {file_name}" in card_info["body"]


def test_invalid_global_custom_rule(application, request):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Upload invalid global custom role file
            2. Check number of rules in it
        expectedResults:
            1. Invalid global custom rule file should have 0 rules
    """
    file_name = "customWebLogic.windup.label.xml"
    view = navigate_to(application.collections.globalconfigurations, "Custom")
    view.custom_rules.upload_rule_file(file_name)
    view.table.wait_displayed("20s")

    @request.addfinalizer
    def _finalize():
        view.search.fill("")
        view.custom_rules.delete(file_name)

    all_rules = view.table.read()
    for rule in all_rules:
        if rule["Short path"] == file_name:
            assert int(rule["Number of rules"]) == 0


def test_total_global_system_rule(application):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Navigate to Global > Rules configuration > System rules
            2. Check show all rules
        expectedResults:
            1. Total system rules count should be 331
    """
    view = navigate_to(application.collections.globalconfigurations, "System")
    view.wait_displayed()
    view.show_all_rules.click()
    assert view.paginator.total_items == 331


def test_filter_global_system_rule(application):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Navigate to Global > Rules configuration > System rules
            2. Check show all rules
        expectedResults:
            1. Total system rules count should be 331
    """
    filters = {
        "Source": ["agroal", "amazon", "avro"],
        "Target": ["camel", "cloud-readiness", "quarkus"],
    }
    view = navigate_to(application.collections.globalconfigurations, "System")
    view.wait_displayed()
    view.show_all_rules.click()
    for filter_type in filters:
        for filter_value in filters[filter_type]:
            view.search(search_value=filter_value, filter_type=filter_type)
            filtered_rules = view.table.read()
            for rule in filtered_rules:
                assert rule[filter_type] == filter_value
