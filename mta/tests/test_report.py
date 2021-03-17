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
    """Test filter applications

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Create project and run analysis
            2. Click on report action to see detailed report and select tab - All Applications
            3. Search applications by name or tag
        expectedResults:
            1. It should give results as per search value
    """
    project, project_collection = create_project_with_two_apps
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    view.search("acm", "Name")
    apps_list = view.application_table.get_applications_list
    assert "acmeair-webapp-1.0-SNAPSHOT.war" in apps_list[:-1]
    view.clear_filters()
    view.search("JTA", "Tag")
    apps_list = view.application_table.get_applications_list
    assert "acmeair-webapp-1.0-SNAPSHOT.war" in apps_list[:-1]


def test_sort_application_list(create_project):
    """Test Sorting of applications

    Polarion:
        assignee: nsrivast
        initialEstimate: 1/12h
        caseimportance: medium
        caseposneg: positive
        testtype: functional
        casecomponent: WebConsole
        testSteps:
            1. Create project and run analysis
            2. Click on report action to see detailed report and select tab - All Applications
            3. Sort applications by name or story points
        expectedResults:
            1. It should sort applications as per selected criteria (name or story points)
    """
    project, project_collection = create_project
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    view.sort_by("Name")
    app_list_by_name = view.application_table.get_applications_list
    assert app_list_by_name[:-1] == sorted(app_list_by_name[:-1])
    view.alpha_sort.click()
    app_list_by_name = view.application_table.get_applications_list
    assert app_list_by_name[:-1] == sorted(app_list_by_name[:-1], reverse=True)
    view.sort_by("Story Points")
    app_list_by_story_points = view.application_table.get_applications_list
    app_list_story_points_desc = [
        "bw-note-ear-4.0.0.ear",
        "acmeair-webapp-1.0-SNAPSHOT.war",
        "cadmium-war-0.1.0.war",
    ]
    assert app_list_by_story_points[:-1] == app_list_story_points_desc
    view.alpha_sort.click()
    app_list_story_points_asc = [
        "cadmium-war-0.1.0.war",
        "acmeair-webapp-1.0-SNAPSHOT.war",
        "bw-note-ear-4.0.0.ear",
    ]
    app_list_by_story_points = view.application_table.get_applications_list
    assert app_list_by_story_points[:-1] == app_list_story_points_asc
