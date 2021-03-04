import fauxfactory
import pytest
from wait_for import wait_for

from mta.base.application.implementations.web_ui import navigate_to
from mta.entities import AllProjectView
from mta.entities.analysis_results import AnalysisResultsView
from mta.entities.report import AllApplicationsView
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper
from mta.utils.update import update


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI"], indirect=True)
def test_project_crud(mta_app, create_minimal_project):

    project, project_collection = create_minimal_project
    assert project.exists

    # Edit Project with no change , clicks cancel
    project.update({"name": project.name})
    assert project.name == project.name

    # Edit Project with new description, name and save
    updated_name = fauxfactory.gen_alphanumeric(12, start="edited_")
    update_desc = fauxfactory.gen_alphanumeric(12, start="edited_")
    with update(project):
        project.name = updated_name
        project.description = update_desc

    assert project.exists


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI"], indirect=True)
def test_delete_application(mta_app):
    """
    Test01 -08
    Delete uploaded application file and check if next button gets disabled
    """
    application = mta_app
    project_collection = application.collections.projects
    view = navigate_to(project_collection, "Add")
    view.create_project.fill(
        {"name": fauxfactory.gen_alphanumeric(12, start="project_"), "description": "desc"}
    )

    env = conf.get_config("env")
    fs = FTPClientWrapper(env.ftpserver.entities.mta)
    file_path = fs.download("acmeair-webapp-1.0-SNAPSHOT.war")

    view.add_applications.upload_file.fill(file_path)
    wait_for(lambda: view.add_applications.next_button.is_enabled, delay=0.2, timeout=60)
    assert view.add_applications.next_button.is_enabled
    view.add_applications.delete_application.click()

    view.add_applications.next_button.wait_displayed()
    assert not view.add_applications.next_button.is_enabled
    view.add_applications.back_button.wait_displayed()
    view.add_applications.back_button.click()
    view.add_applications.cancel_button.wait_displayed()
    view.add_applications.cancel_button.click()
    view.create_project.yes_button.click()


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI"], indirect=True)
def test_application_report(mta_app, create_minimal_project):
    project, project_collection = create_minimal_project
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    assert view.is_displayed
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    assert view.is_displayed


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI"], indirect=True)
def test_sort_projects(
    mta_app, create_minimal_project, create_project_with_two_apps, create_project
):
    """
    Sort Projects
    """
    project1, project_collection = create_minimal_project
    assert project1.exists

    project2, project_collection = create_project_with_two_apps
    assert project2.exists

    project3, project_collection = create_project
    assert project3.exists

    project_collection.sort_projects("Name", "ascending")
    project_collection.sort_projects("Applications", "ascending")
    project_collection.sort_projects("Status", "ascending")
    project_collection.sort_projects("Name", "descending")
    project_collection.sort_projects("Applications", "descending")
    project_collection.sort_projects("Status", "descending")


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI"], indirect=True)
def test_search_project(mta_app, create_minimal_project):
    """
    Search Projects
    """
    project, project_collection = create_minimal_project
    assert project.exists
    project_collection.search_project(project.name)
    view = project_collection.create_view(AllProjectView)
    assert project.name in [row.name.text for row in view.table]
