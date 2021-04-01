import pytest

from mta.base.application.implementations.web_ui import navigate_to
from mta.entities.analysis_results import AnalysisResults
from mta.entities.global_config.labels_configuration import CustomLabelsConfigurations
from mta.entities.global_config.labels_configuration import CustomLabelsView
from mta.entities.global_config.labels_configuration import SystemLabelsConfigurations
from mta.entities.global_config.labels_configuration import SystemLabelsView


@pytest.fixture(scope="function")
def add_global_custom_label(application):
    """This fixture with upload global custom label file"""
    file_name = "customWebLogic.windup.label.xml"
    labels_configurations = CustomLabelsConfigurations(application, file_name)
    labels_configurations.upload_custom_label_file()
    view = labels_configurations.create_view(CustomLabelsView)
    view.table.wait_displayed("20s")
    yield file_name, view, labels_configurations
    labels_configurations.delete_custom_label_file()


def test_crud_global_custom_label(application):
    """ Test to upload global custom labels file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Login to MTA web console
            2. Navigate to Global > Rules configuration > Custom Labels
            3. Click on Add label button and browse label file
            4. Click on Close button
        expectedResults:
            1. Custom label file should be listed in table
    """
    file_name = "customWebLogic.windup.label.xml"
    global_configurations = CustomLabelsConfigurations(application, file_name)
    global_configurations.upload_custom_label_file()
    view = global_configurations.create_view(CustomLabelsView)
    view.table.wait_displayed("20s")
    assert file_name in [label["Short path"] for label in view.table.read()]
    assert global_configurations.delete_custom_label_file()


def test_search_global_custom_label(add_global_custom_label):
    """ Test to search global custom labels file from table

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Login to MTA web console
            2. Navigate to Global > Labels configuration > Custom labels
            3. Click on Add label button and browse labels files
            4. Click on Close button
            5. Add value in 'Filter by short path' input box and hit enter
        expectedResults:
            1. Custom labels file should searched by substring
    """
    file_name, view, labels_configurations = add_global_custom_label
    view.table.wait_displayed("20s")
    view.search.fill("custom")

    assert file_name in [label["Short path"] for label in view.table.read()]
    view.search.fill("custom-invalid")
    try:
        assert file_name not in [label["Short path"] for label in view.table.read()]
    except IndexError:
        view.search.fill("")
        pass


def test_analysis_global_custom_label(application, add_global_custom_label, create_minimal_project):
    """ Test to upload global custom labels file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Upload global custom labels file
            2. Create project and run analysis
            3. Go to analysis details page and check if custom labels contains global scope custom
               label file
        expectedResults:
            1. Analysis should be completed successfully
    """
    file_name, view, labels_configurations = add_global_custom_label

    project, project_collection = create_minimal_project
    analysis_results = AnalysisResults(application, project.name)
    view = navigate_to(analysis_results, "AnalysisDetailsPage")
    view.custom_labels.wait_displayed("30s")
    card_info = view.custom_labels.read()
    assert file_name in card_info["body"].split("Global")[1]


def test_invalid_label_file_type(application, request):
    """ Test to upload global custom label file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Upload invalid global custom label file
            2. Check number of labels in it
        expectedResults:
            1. Invalid global custom label file should have 0 labels
    """
    file_name = "custom.Test1rules.rhamt.xml"
    labels_configurations = CustomLabelsConfigurations(application, file_name)
    labels_configurations.upload_custom_label_file()
    view = labels_configurations.create_view(CustomLabelsView)
    view.table.wait_displayed("20s")

    @request.addfinalizer
    def _finalize():
        view.search.fill("")
        labels_configurations.delete_custom_label_file()

    all_labels = view.table.read()
    for label in all_labels:
        if label["Short path"] == file_name:
            assert int(label["Number of labels"]) == 0


def test_total_global_system_label(application):
    """ Test to upload global custom label file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Navigate to Global > Labels configuration > System labels
            2. Check show all labels
        expectedResults:
            1. Total system labels count should be equal or greater than 1
    """
    global_configurations = SystemLabelsConfigurations(application)
    view = navigate_to(global_configurations, "SystemLabel")
    view.wait_displayed()
    assert view.paginator.total_items >= 1


def test_search_global_system_label(application):
    """ Test to upload global custom label file

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Navigate to Global > Labels configuration > System labels
            2. Search by label's provider ID
        expectedResults:
            1. It should list label with that provider ID
    """
    global_configurations = SystemLabelsConfigurations(application)
    global_configurations.search_system_labels("core")
    view = global_configurations.create_view(SystemLabelsView)
    data = view.table.read()[0]
    assert data["Provider ID"] == "core_labels"
