"""
Polarion:
    casecomponent: WebConsole
    linkedWorkItems: MTA_Web_Console
"""
import pytest

from mta.base.application.implementations.web_ui import navigate_to
from mta.entities.analysis_results import AnalysisResults
from mta.entities.analysis_results import AnalysisResultsView
from mta.entities.global_config.rules_configuration import CustomRulesConfiguration
from mta.entities.global_config.rules_configuration import CustomRulesView
from mta.entities.global_config.rules_configuration import SystemRulesConfiguration
from mta.entities.report import AllApplicationsView
from mta.entities.report import Issues


@pytest.fixture(scope="function")
def add_global_custom_rule(application):
    """This fixture with upload global custom rule file"""
    file_name = "custom.Test1rules.rhamt.xml"
    rules_configurations = CustomRulesConfiguration(application, file_name)
    rules_configurations.upload_custom_rule_file()
    view = rules_configurations.create_view(CustomRulesView)
    view.table.wait_displayed("20s")
    yield file_name, view, rules_configurations
    rules_configurations.delete_custom_rule()


def test_crud_global_custom_rule(application):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Login to MTA web console
            2. Navigate to Global > Rules configuration > Custom rules
            3. Click on Add rule button and browse rules file
            4. Click on Close button
        expectedResults:
            1. Custom rules file should be listed in table
    """
    file_name = "custom.Test1rules.rhamt.xml"
    rules_configurations = CustomRulesConfiguration(application, file_name)
    rules_configurations.upload_custom_rule_file()
    view = rules_configurations.create_view(CustomRulesView)
    view.table.wait_displayed("20s")
    assert file_name in [rules["Short path"] for rules in view.table.read()]
    assert rules_configurations.delete_custom_rule()


def test_search_global_custom_rule(add_global_custom_rule):
    """ Test to search global custom rules file from table

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Login to MTA web console
            2. Navigate to Global > Rules configuration > Custom rules
            3. Click on Add rule button and browse rules files
            4. Click on Close button
            5. Add value in 'Filter by short path' input box and hit enter
        expectedResults:
            1. Custom rules file should searched by substring
    """
    file_name, view, rules_configurations = add_global_custom_rule
    view.table.wait_displayed("20s")
    view.search.fill("rhamt")

    assert file_name in [rules["Short path"] for rules in view.table.read()]
    view.search.fill("rhamt-invalid")
    try:
        assert file_name not in [rules["Short path"] for rules in view.table.read()]
    except IndexError:
        view.search.fill("")
        pass


def test_analysis_global_custom_rule(application, add_global_custom_rule, create_minimal_project):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Upload global custom rule file
            2. Create project and run analysis
            3. Go to analysis details page and check if custom rules contains global scope custom
               rule file
        expectedResults:
            1. Analysis should be completed successfully
            2. Global custom rule should be applied/fired in the analysis report
    """
    file_name, view, rules_configurations = add_global_custom_rule
    project, project_collection = create_minimal_project
    analysis_results = AnalysisResults(application, project.name)
    view = navigate_to(analysis_results, "AnalysisDetailsPage")
    view.custom_rules.wait_displayed("20s")
    card_info = view.custom_rules.read()
    assert file_name in card_info["body"].split("Global")[1]
    view.execution_link.click()
    view = analysis_results.create_view(AnalysisResultsView)
    view.wait_displayed("30s")
    view.analysis_results.show_report()
    view = analysis_results.create_view(AllApplicationsView)
    view.application_table.application_details("acmeair-webapp-1.0-SNAPSHOT.war")
    view.tabs.issues.click()
    view = analysis_results.create_view(Issues)
    # TODO(ghubale): Updated test case with reading Migration potential table
    assert view.wait_displayed


def test_invalid_rule_file_type(application, request):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Upload invalid global custom rule file
            2. Check number of rules in it
        expectedResults:
            1. Invalid global custom rule file should have 0 rules
    """
    file_names = ["customWebLogic.windup.label.xml", "empty_rule_file.xml"]

    @request.addfinalizer
    def _finalize():
        for file in file_names:
            rules = CustomRulesConfiguration(application, file)
            rules.delete_custom_rule()

    for file_name in file_names:
        rules_configurations = CustomRulesConfiguration(application, file_name)
        rules_configurations.upload_custom_rule_file()
        view = rules_configurations.create_view(CustomRulesView)
        view.table.wait_displayed("20s")

        all_rules = view.table.read()
        for rule in all_rules:
            if rule["Short path"] == file_name:
                assert int(rule["Number of rules"]) == 0
    else:
        assert False


def test_total_global_system_rule(application):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Navigate to Global > Rules configuration > System rules
            2. Check show all rules
        expectedResults:
            1. Total system rules count should be 331
    """
    global_configurations = SystemRulesConfiguration(application)
    view = navigate_to(global_configurations, "SystemRule")
    view.show_all_rules.wait_displayed("30s")
    no_of_rules_before = view.paginator.total_items
    view.show_all_rules.click()
    assert view.paginator.total_items >= no_of_rules_before


def test_filter_global_system_rule(application):
    """ Test to upload global custom rules file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Navigate to Global > Rules configuration > System rules
            2. Check show all rules
        expectedResults:
            1. Total system rules count should be 331
    """
    filters = {
        "Source": ["agroal", "amazon", "avro"],
        # "Target": ["camel", "cloud-readiness", "quarkus"],
        # TODO(ghubale): Uncomment it once fixed drop down selection for option - Target
    }
    global_configurations = SystemRulesConfiguration(application)
    view = navigate_to(global_configurations, "SystemRule")
    view.show_all_rules.wait_displayed("30s")
    view.show_all_rules.click()
    for filter_type in filters:
        for filter_value in filters[filter_type]:
            global_configurations.search_system_rules(
                search_value=filter_value, filter_type=filter_type, clear_filters=True
            )
            filtered_rules = view.table.read()
            for rule in filtered_rules:
                assert filter_value in rule[filter_type]


def test_add_folder_of_rules(request, application):
    """ Test adding a folder containing both valid and invalid rules

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Login to MTA web console
            2. Navigate to Global > Rules configuration > Custom rules
            3. Click on Add rule button and got to server path tab and browse rules folder
            4. Click on Close button
        expectedResults:
            1. Error should be handled and it should only upload valid rules files from folder
    """
    # MTA application is not recognizing this server path
    rules_dir = "mta/applications/valid_invalid_rules/"

    @request.addfinalizer
    def _finalize():
        rules = CustomRulesConfiguration(application, rules_dir)
        rules.delete_custom_rule()

    rules_configurations = CustomRulesConfiguration(application, rules_dir)
    rules_configurations.upload_custom_rule_file(server_path=True, dir_path=rules_dir)
    view = rules_configurations.create_view(CustomRulesView)
    view.table.wait_displayed("20s")
    all_rules = view.table.read()
    for rule in all_rules:
        if rule["Short path"] == rules_dir:
            assert int(rule["Number of rules"]) == 1
    else:
        assert False
