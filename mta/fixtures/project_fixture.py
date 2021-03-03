import fauxfactory
import pytest


@pytest.fixture(scope="session")
def mta_app(application, request):
    context = getattr(request, "param", "ViaOperatorUI")
    application.mta_context = context
    return application


@pytest.fixture(scope="function")
def create_minimal_project(mta_app):
    project_collection = mta_app.collections.projects
    project = project_collection.create(
        name=fauxfactory.gen_alphanumeric(12, start="project_"),
        description=fauxfactory.gen_alphanumeric(start="desc_"),
        app_list=["acmeair-webapp-1.0-SNAPSHOT.war"],
    )
    yield project, project_collection
    project.delete_if_exists()


@pytest.fixture(scope="function")
def create_project_with_two_apps(mta_app):
    app_list = ["acmeair-webapp-1.0-SNAPSHOT.war", "arit-ear-0.8.1-SNAPSHOT.ear"]
    project_collection = mta_app.collections.projects
    project = project_collection.create(
        name=fauxfactory.gen_alphanumeric(12, start="project_"),
        description=fauxfactory.gen_alphanumeric(start="desc_"),
        app_list=app_list,
        transformation_path="Containerization",
    )
    yield project, project_collection
    project.delete_if_exists()


@pytest.fixture(scope="function")
def create_project(mta_app):
    project_collection = mta_app.collections.projects
    project = project_collection.create(
        name=fauxfactory.gen_alphanumeric(12, start="project_"),
        description=fauxfactory.gen_alphanumeric(start="desc_"),
        app_list=[
            "acmeair-webapp-1.0-SNAPSHOT.war",
            "cadmium-war-0.1.0.war",
            "bw-note-ear-4.0.0.ear",
        ],
        transformation_path="Containerization",
    )
    yield project, project_collection
    project.delete_if_exists()
