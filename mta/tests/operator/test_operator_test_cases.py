"""
Polarion:
    casecomponent: WebConsole
    linkedWorkItems: MTA_Web_Console
"""
import fauxfactory
from wait_for import wait_for

from mta.base.application.implementations.web_ui import navigate_to
from mta.entities.analysis_results import AnalysisResultsView
from mta.entities.report import AllApplicationsView
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper
from mta.utils.update import update


def test_ocp_project_crud(create_minimal_project):
    """
    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        testSteps:
            1. Create project
            2. Edit project name or description
            3. Click on delete action button or select delete option from kebab drop down
        expectedResults:
            1. Project should be created properly
            2. Project name or description should be updated properly
            3. Project should get deleted
    """
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


def test_ocp_delete_application(mta_app):
    """Delete uploaded application file and check if next button gets disabled

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Go to project all page and click on `Create project` button
            2. Add name and description and click on `Next` button
            3. Browse and add application file
            4. Click on delete button
        expectedResults:
            1. Next button should be disabled before uploading application file
            1. Next button should be enabled after uploading application file
            2. Next button should be disabled after deleting application file
    """
    application = mta_app
    project_collection = application.collections.projects
    view = navigate_to(project_collection, "Add")
    view.wait_displayed("20s")
    view.create_project.fill(
        {"name": fauxfactory.gen_alphanumeric(12, start="project_"), "description": "desc"}
    )
    view.add_applications.wait_displayed()
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


def test_ocp_application_report(create_minimal_project, request):
    """
    Polarion:
        assignee: ghubalemta_app
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project and run analysis
            2. Click on `report` action button
        expectedResults:
            1. It should show report analysis in detail page
    """
    project, project_collection = create_minimal_project
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    assert view.is_displayed
    view.analysis_results.show_report(request)
    view = project_collection.create_view(AllApplicationsView)
    view.wait_displayed("40s")
    assert view.is_displayed
