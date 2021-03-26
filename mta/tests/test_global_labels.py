import fauxfactory
import pytest

from mta.base.application.implementations.web_ui import navigate_to
from mta.entities.analysis_results import AnalysisResults


@pytest.fixture(scope="function")
def add_global_custom_label(application):
    """This fixture with upload global custom label file"""
    file_name = "customWebLogic.windup.label.xml"
    view = navigate_to(application.collections.globalconfigurations, "CustomLabel")
    view.custom_labels.upload_label_file(file_name)
    view.table.wait_displayed("20s")
    return file_name


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
    view = navigate_to(application.collections.globalconfigurations, "CustomLabel")
    view.custom_labels.upload_label_file(file_name)
    view.table.wait_displayed("20s")
    assert file_name in [label["Short path"] for label in view.table.read()]
    assert view.custom_labels.delete(file_name)


def test_search_global_custom_label(application, request):
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
    file_name = "customWebLogic.windup.label.xml"
    view = navigate_to(application.collections.globalconfigurations, "CustomLabel")
    view.custom_labels.upload_label_file(file_name)
    view.table.wait_displayed("20s")
    view.search.fill("custom")

    @request.addfinalizer
    def _finalize():
        view.search.fill("")
        view.custom_labels.delete(file_name)

    assert file_name in [label["Short path"] for label in view.table.read()]
    view.search.fill("custom-invalid")
    try:
        assert file_name not in [label["Short path"] for label in view.table.read()]
    except IndexError:
        pass


def test_analysis_global_custom_label(application, request, add_global_custom_label):
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
    file_name = add_global_custom_label
    project = application.collections.projects.create(
        name=fauxfactory.gen_alphanumeric(12, start="project_"),
        description=fauxfactory.gen_alphanumeric(start="desc_"),
        app_list=["acmeair-webapp-1.0-SNAPSHOT.war"],
    )
    assert project.exists
    request.addfinalizer(project.delete_if_exists)
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
    view = navigate_to(application.collections.globalconfigurations, "CustomLabel")
    view.custom_labels.upload_label_file(file_name)
    view.table.wait_displayed("20s")

    @request.addfinalizer
    def _finalize():
        view.search.fill("")
        view.custom_labels.delete(file_name)

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
    view = navigate_to(application.collections.globalconfigurations, "SystemLabel")
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
    view = navigate_to(application.collections.globalconfigurations, "SystemLabel")
    view.search.wait_displayed("30s")
    view.search.fill("core")
    data = view.table.read()[0]
    assert data["Provider ID"] == "core_labels"
