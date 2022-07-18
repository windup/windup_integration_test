"""
Polarion:
    casecomponent: WebConsole
    linkedWorkItems: MTA_Web_Console
"""
import pytest

from mta.base.application.implementations.web_ui import navigate_to
from mta.entities.global_config.rules_configuration import CustomRulesConfiguration
from mta.entities.global_config.rules_configuration import CustomRulesView
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper


@pytest.mark.parametrize("mta_app", ["ViaWebUI"], indirect=True)
def test_add_folder_of_rules(mta_app, request):
    """Test adding a folder containing both valid and invalid rules

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
