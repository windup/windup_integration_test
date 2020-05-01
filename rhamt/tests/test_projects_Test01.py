import fauxfactory

from rhamt.base.application.implementations.web_ui import navigate_to
from rhamt.entities.analysis_results import AnalysisResultsView
from rhamt.entities.report import AllApplicationsView
from rhamt.utils import conf
from rhamt.utils.ftp import FTPClientWrapper
from rhamt.utils.update import update


def test_project_crud(application):
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = application.collections.projects
    # TO DO paramterize the test later for file_name and trans_path, hardcoding for now
    project = project_collection.create(
        name=project_name,
        description=fauxfactory.gen_alphanumeric(),
        app_list=["acmeair-webapp-1.0-SNAPSHOT.war"],
        transformation_path="Containerization",
    )
    assert project.exists(project_name)

    # Edit Project with no change , clicks cancel
    project.update({"name": project_name})
    assert project.name == project_name

    # Edit Project with new desc and save
    update_descr = "my edited description"
    with update(project):
        project.description = update_descr
    assert project.description == update_descr

    # Delete project
    project.delete(project_name)
    assert not project.exists(project_name)


def test_delete_application(application):
    """
    Test01 -08
    Delete uploaded application file and check if next button gets disabled
    """
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = application.collections.projects
    view = navigate_to(project_collection, "Add")
    view.create_project.fill({"name": project_name, "description": "desc"})

    env = conf.get_config("env")
    fs = FTPClientWrapper(env.ftpserver.entities.rhamt)
    file_path = fs.download("acmeair-webapp-1.0-SNAPSHOT.war")

    view.add_applications.upload_file.fill(file_path)
    view.add_applications.next_btn.wait_displayed()
    view.add_applications.delete_application.click()

    view.add_applications.confirm_delete.wait_displayed()
    view.add_applications.confirm_delete.click()

    view.add_applications.next_btn.wait_displayed()
    assert not view.add_applications.next_btn.is_enabled


def test_application_report(application):
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = application.collections.projects
    # TO DO paramterize the test later for file_name and trans_path, hardcoding for now
    project_collection.create(
        name=project_name,
        description=fauxfactory.gen_alphanumeric(),
        app_list=["acmeair-webapp-1.0-SNAPSHOT.war"],
    )
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    assert view.is_displayed
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    assert view.is_displayed
