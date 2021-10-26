"""
Polarion:
    casecomponent: WebConsole
    linkedWorkItems: MTA_Web_Console
"""
import fauxfactory
import pytest

from mta.entities.analysis_results import AnalysisResultsView
from mta.entities.report import AllApplicationsView
from mta.entities.report import HardCodedIP


# @pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI", "ViaSecure"], indirect=True)
def test_send_feedback_and_validate_url(mta_app, create_minimal_project):
    """Test send feedback

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        testSteps:
            1. Create project and run analysis
            2. Click on report action to see detailed report
            3. Click on `Send Feedback` button
        expectedResults:
            1. It should open feedback window
            2. Report URL should have mta-ui/api/static-report
    """
    project, project_collection = create_minimal_project
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    view.analysis_results.show_report()
    # Validate URL report has mta-ui/api/static-report
    url = "/mta-ui/api/static-report"
    assert url in mta_app.web_ui.widgetastic_browser.url
    view = project_collection.create_view(AllApplicationsView)
    view.send_feedback.click()


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI", "ViaSecure"], indirect=True)
def test_filter_application_list(mta_app, create_project_with_two_apps):
    """Test filter applications

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
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


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI", "ViaSecure"], indirect=True)
def test_sort_application_list(mta_app, create_project):
    """Test Sorting of applications

    Polarion:
        assignee: nsrivast
        initialEstimate: 1/12h
        caseimportance: medium
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


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI", "ViaSecure"], indirect=True)
def test_hard_code_ip_report(request, mta_app):
    """Test send feedback

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        testSteps:
            1. Create project and run analysis for "AdministracionEfectivo.ear" app with target
               "Containerization"
            2. Click on report action to see detailed report
            3. Click on application for detailed application analysis report
        expectedResults:
            1. Analysis report should show Hard-Coded IP Addresses report generated
    """
    app_name = "AdministracionEfectivo.ear"
    project_collection = mta_app.collections.projects
    project = project_collection.create(
        name=fauxfactory.gen_alphanumeric(12, start="project_"),
        description=fauxfactory.gen_alphanumeric(start="desc_"),
        app_list=[app_name],
        transformation_path="Containerization",
    )
    request.addfinalizer(project.delete_if_exists)
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    view.application_table.application_details(app_name)
    view.tabs.hard_coded_ip.click()
    view = project_collection.create_view(HardCodedIP)
    assert view.wait_displayed


@pytest.mark.manual
def test_all_links_in_report_generated():
    """Test all links accessible or not in report generated

    Polarion:
        assignee: nsrivast
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project and run analysis
            2. Click on report action to see detailed report
            3. Check on application name and check all links if reachable or not.
        expectedResults:
            1. All links should be valid and accessible.
    """
    pass
