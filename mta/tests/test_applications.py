from mta.entities.applications import Applications
from mta.entities.applications import ApplicationsView


def test_applications_page(application, create_project):
    """ Validates Web console Test 03
    1) Upload more than one application into a project to analyse
    2) Go to Applications page
    2) Search app
    3) Delete app
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


def test_add_applications_to_project(application, create_minimal_project):
    """ Validates Web console Test 03
    1) Upload one application into a project to analyse
    2) Go to Applications page
    3) Add another app
    """
    project, project_collection = create_minimal_project
    assert project.exists
    applications = Applications(application, project.name)
    applications.add_application(app="cadmium-war-0.1.0.war")


def test_delete_application_from_project(application, create_project_with_two_apps):
    """ Validates Web console Test 03
    1) Upload one or more application into a project to analyse
    2) Go to Applications page
    3) Delete app
    """
    project, project_collection = create_project_with_two_apps
    assert project.exists
    applications = Applications(application, project.name)
    # Delete and Cancel
    applications.delete_application(name="acmeair-webapp-1.0-SNAPSHOT.war", cancel=True)
    # Delete
    applications.delete_application(name="acmeair-webapp-1.0-SNAPSHOT.war", cancel=False)


def test_sort_applications(application, create_project_with_two_apps):
    """ Validates Web console Test 03
    1) Upload one or more application into a project to analyse
    2) Go to Applications page
    3) Sort app
    """
    project, project_collection = create_project_with_two_apps
    assert project.exists
    applications = Applications(application, project.name)
    # Sort application
    applications.sort_application("Application", "ascending")
