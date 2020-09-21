import fauxfactory

from mta.entities.applications import Applications
from mta.entities.applications import ApplicationsView


def test_applications(application):
    """ Validates Web console Test 03
    1) Upload more than one application into a project to analyse
    2) Go to Applications page
    2) Search app
    3) Delete app
    """
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = application.collections.projects
    project = project_collection.create(
        name=project_name,
        description=fauxfactory.gen_alphanumeric(),
        app_list=[
            "acmeair-webapp-1.0-SNAPSHOT.war",
            "arit-ear-0.8.1-SNAPSHOT.ear",
            "cadmium-war-0.1.0.war",
        ],
        transformation_path="Containerization",
    )
    assert project.exists
    applications = Applications(application, project_name)
    view = applications.create_view(ApplicationsView)

    # search app in list
    applications.search_application(name="acmeair-webapp-1.0-SNAPSHOT.war")
    assert view.application_row(
        name="acmeair-webapp-1.0-SNAPSHOT.war"
    ).application_name.is_displayed
    view.clear_search()
    # search row 2 in list
    applications.search_application(name="cadmium-war-0.1.0.war")
    assert view.application_row(name="cadmium-war-0.1.0.war").application_name.is_displayed
    view.clear_search()


def test_add_application(application):
    """ Validates Web console Test 03
    1) Upload one application into a project to analyse
    2) Go to Applications page
    3) Add another app
    """
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = application.collections.projects
    project = project_collection.create(
        name=project_name,
        description=fauxfactory.gen_alphanumeric(),
        app_list=["acmeair-webapp-1.0-SNAPSHOT.war"],
        transformation_path="Containerization",
    )
    assert project.exists
    applications = Applications(application, project_name)
    applications.add_application(app="cadmium-war-0.1.0.war")


def test_delete_application(application):
    """ Validates Web console Test 03
    1) Upload one or more application into a project to analyse
    2) Go to Applications page
    3) Delete app
    """
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = application.collections.projects
    project = project_collection.create(
        name=project_name,
        description=fauxfactory.gen_alphanumeric(),
        app_list=[
            "acmeair-webapp-1.0-SNAPSHOT.war",
            "arit-ear-0.8.1-SNAPSHOT.ear",
            "cadmium-war-0.1.0.war",
        ],
        transformation_path="Containerization",
    )
    assert project.exists
    applications = Applications(application, project_name)
    # Delete and Cancel
    applications.delete_application(name="cadmium-war-0.1.0.war", cancel=True)
    # Delete
    applications.delete_application(name="cadmium-war-0.1.0.war", cancel=False)


def test_sort_application(application):
    """ Validates Web console Test 03
    1) Upload one or more application into a project to analyse
    2) Go to Applications page
    3) Sort app
    """
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = application.collections.projects
    project = project_collection.create(
        name=project_name,
        description=fauxfactory.gen_alphanumeric(),
        app_list=[
            "acmeair-webapp-1.0-SNAPSHOT.war",
            "cadmium-war-0.1.0.war",
            "arit-ear-0.8.1-SNAPSHOT.ear",
        ],
    )
    assert project.exists
    applications = Applications(application, project_name)
    view = applications.create_view(ApplicationsView)
    # Sort application
    applications.sort_application()
    assert view.application_row(name=1).row.text < view.application_row(name=2).row.text
