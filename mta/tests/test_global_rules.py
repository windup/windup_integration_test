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
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper


@pytest.fixture(scope="function")
def add_global_custom_rule(mta_app):
    """This fixture with upload global custom rule file"""
    file_name = "custom.Test1rules.rhamt.xml"
    rules_configurations = CustomRulesConfiguration(mta_app, file_name)
    rules_configurations.upload_custom_rule_file()
    view = rules_configurations.create_view(CustomRulesView)
    view.wait_displayed("20s")
    yield file_name, view, rules_configurations
    rules_configurations.delete_custom_rule()
    view.logout()


@pytest.mark.parametrize("mta_app", ["ViaOperatorUI", "ViaSecure", "ViaWebUI"], indirect=True)
def test_crud_global_custom_rule(mta_app, add_global_custom_rule):
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
    file_name, view, rules_configurations = add_global_custom_rule
    assert file_name in [rules["Short path"] for rules in view.table.read()]


@pytest.mark.parametrize("mta_app", ["ViaOperatorUI"], indirect=True)
def test_search_global_custom_rule(mta_app, add_global_custom_rule):
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
    view.wait_displayed("20s")

    view.search.fill("rhamt")
    view.wait_displayed("10s")
    view.search.fill("rhamt-invalid")
    view.table_loaded()
    try:
        assert file_name not in [rules["Short path"] for rules in view.table.read()]
    except IndexError:
        view.search.fill("")
        pass


@pytest.mark.parametrize("mta_app", ["ViaOperatorUI", "ViaSecure", "ViaWebUI"], indirect=True)
def test_analysis_global_custom_rule(
    mta_app, add_global_custom_rule, create_minimal_project, request
):
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
    analysis_results = AnalysisResults(mta_app, project.name)
    view = navigate_to(analysis_results, "AnalysisDetailsPage")
    view.custom_rules.wait_displayed("20s")
    card_info = view.custom_rules.read()
    assert file_name in card_info["body"].split("Global")[1]
    view.execution_link.click()
    view = analysis_results.create_view(AnalysisResultsView)
    view.wait_displayed("30s")
    view.analysis_results.show_report(request)
    view = analysis_results.create_view(AllApplicationsView)
    view.application_table.application_details("acmeair-webapp-1.0-SNAPSHOT.war")
    view.tabs.issues.click()
    view = analysis_results.create_view(Issues)
    # TODO(ghubale): Update test case with reading Migration potential table
    assert view.wait_displayed


@pytest.mark.parametrize("mta_app", ["ViaOperatorUI", "ViaSecure", "ViaWebUI"], indirect=True)
def test_invalid_rule_file_type(mta_app, request):
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
            rules = CustomRulesConfiguration(mta_app, file)
            rules.delete_custom_rule()
        view.logout()

    for file_name in file_names:
        rules_configurations = CustomRulesConfiguration(mta_app, file_name)
        rules_configurations.upload_custom_rule_file()
        view = rules_configurations.create_view(CustomRulesView)
        view.wait_displayed("5s")

        all_rules = view.table.read()
        for rule in all_rules:
            if rule["Short path"] == file_name:
                assert int(rule["Number of rules"]) == 0


@pytest.mark.parametrize("mta_app", ["ViaOperatorUI", "ViaSecure", "ViaWebUI"], indirect=True)
def test_total_global_system_rule(mta_app, request):
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

    @request.addfinalizer
    def _finalize():
        # Reset view else the URL does not change
        view.logout()

    global_configurations = SystemRulesConfiguration(mta_app)
    view = navigate_to(global_configurations, "SystemRule")
    view.show_all_rules.wait_displayed("30s")
    no_of_rules_before = view.paginator.total_items
    view.show_all_rules.click()
    assert view.paginator.total_items >= no_of_rules_before


@pytest.mark.parametrize("mta_app", ["ViaOperatorUI", "ViaSecure", "ViaWebUI"], indirect=True)
def test_filter_global_system_rule(mta_app, request):
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

    @request.addfinalizer
    def _finalize():
        # Reset view else the URL does not change
        view.logout()

    global_configurations = SystemRulesConfiguration(mta_app)
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


@pytest.mark.parametrize("mta_app", ["ViaWebUI"], indirect=True)
def test_add_folder_of_rules(mta_app, request):
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
    rule_files = [
        "customWebLogic.windup.label.xml",
        "empty_rule_file.xml",
        "custom.Test1rules.rhamt.xml",
    ]
    server_path = "/tmp"

    @request.addfinalizer
    def _finalize():
        rules = CustomRulesConfiguration(mta_app, server_path)
        rules.delete_custom_rule()

    rules_configurations = CustomRulesConfiguration(mta_app, server_path)
    view = navigate_to(rules_configurations, "Add")
    view.wait_displayed("20s")

    for file_name in rule_files:
        env = conf.get_config("env")
        fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
        fs1.download(file_name)

    view.server_path.click()
    view.server_path.rules_path.fill(server_path)
    view.server_path.scan_recursive.click()
    view.server_path.save_button.click()
    view = rules_configurations.create_view(CustomRulesView)
    view.wait_displayed("50s")
    all_rules = view.table.read()
    for rule in all_rules:
        if rule["Short path"] == "/tmp":
            # There will be older files downloaded in /tmp directory. Hence asserting number of
            # rules equal to and greater than 1 only
            assert int(rule["Number of rules"]) >= 1
