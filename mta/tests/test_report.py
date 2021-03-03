from mta.entities.analysis_results import AnalysisResultsView
from mta.entities.report import AllApplicationsView


def test_send_feedback(create_minimal_project):
    """Test send feedback

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Create project and run analysis
            2. Click on report action to see detailed report
            3. Click on `Send Feedback` button
        expectedResults:
            1. It should open feedback window
    """
    project, project_collection = create_minimal_project
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    view.send_feedback.click()


def test_filter_application_list(create_project_with_two_apps):
    """
    Test filter applications
    """
    project, project_collection = create_project_with_two_apps
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    view.search("acm", "Name")
    apps_list = view.get_applications_list
    assert "acmeair-webapp-1.0-SNAPSHOT.war" in apps_list[:-1]
    view.clear_filters
    view.search("JTA", "Tag")
    apps_list = view.get_applications_list
    assert "acmeair-webapp-1.0-SNAPSHOT.war" in apps_list[:-1]
