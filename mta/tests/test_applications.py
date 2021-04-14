"""
Polarion:
    casecomponent: WebConsole
    linkedWorkItems: MTA_Web_Console
"""
import pytest

from mta.entities.applications import Applications
from mta.entities.applications import ApplicationsView


def test_applications_page(application, create_project):
    """ Test search applications

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project with multiple applications files
            2. Go to applications page
            3. Search applications by full name or substring
            4. Delete any application and search by it's name
        expectedResults:
            1. It should show only those applications files matching search string
            2. Deleted application should not be visible in search results
    """
    project, project_collection = create_project
    assert project.exists
    applications = Applications(application, project.name)
    view = applications.create_view(ApplicationsView)
    # search app in list
    applications.search_application(name="acmeair-webapp-1.0-SNAPSHOT.war")
    for row in view.table:
        assert row.application.text == "acmeair-webapp-1.0-SNAPSHOT.war"
    view.clear_search()
    # search row 2 in list
    applications.search_application(name="cadmium-war-0.1.0.war")
    for row in view.table:
        assert row.application.text == "cadmium-war-0.1.0.war"
    view.clear_search()


# Bug WINDUP-2995 Fail
@pytest.mark.skip(reason="MTA UI Issue - WINDUP-2995")
def test_add_applications_to_project(application, create_minimal_project):
    """ Test add applications

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project and add a application file
            2. Go to applications page and add new application file
            3. Go to `Analysis configuration` page and run analysis
        expectedResults:
            1. It should be added successfully
            2. Analysis should get complete successfully
    """
    # TODO(ghubale): Step 3 is skipped due to issue - WINDUP-2995
    project, project_collection = create_minimal_project
    assert project.exists

    applications = Applications(application, project.name)
    applications.add_application(app="cadmium-war-0.1.0.war")


def test_delete_application_from_project(application, create_project_with_two_apps):
    """ Test delete application from project

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project and add multiple application files
            2. Go to applications page
            3. Delete application files
            4. Delete cancel application files
        expectedResults:
            1. It should be deleted successfully
            2. On canceling application delete. It should navigate to applications all page
    """
    project, project_collection = create_project_with_two_apps
    assert project.exists
    applications = Applications(application, project.name)
    # Delete and Cancel
    applications.delete_application(name="acmeair-webapp-1.0-SNAPSHOT.war", cancel=True)
    # Delete
    applications.delete_application(name="acmeair-webapp-1.0-SNAPSHOT.war", cancel=False)


def test_sort_applications(application, create_project_with_two_apps):
    """ Test sort applications

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project and add multiple application files
            2. Go to applications page
            3. Sort applications by
                {"Application" > "ascending" and "descending",
                 "Date added" > "ascending" and "descending"}
        expectedResults:
            1. All values should get sorted properly
    """
    project, project_collection = create_project_with_two_apps
    assert project.exists
    applications = Applications(application, project.name)
    # Sort application
    applications.sort_application("Application", "ascending")


def test_application_name_advanced_option():
    """ Test application name under advanced options

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project and while creating project give application name
            2. Application name input present on advanced options page. Provide name and 'save and
               run analysis".
            4. Go to analysis results page and click on actions - 'Reports'
            5. Check if you can see application on report's details page
        expectedResults:
            1. It should show provided name
    """
    pass
