"""
Polarion:
    casecomponent: WebConsole
    linkedWorkItems: MTA_Web_Console
"""
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


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI", "ViaSecure"], indirect=True)
def test_project_crud(mta_app, create_minimal_project):
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


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI", "ViaSecure"], indirect=True)
def test_delete_application(mta_app):
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


@pytest.mark.parametrize("mta_app", ["ViaWebUI", "ViaOperatorUI", "ViaSecure"], indirect=True)
def test_application_report(mta_app, create_minimal_project):
    """
    Polarion:
        assignee: ghubale
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
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    assert view.is_displayed


@pytest.mark.parametrize("mta_app", ["ViaWebUI"], indirect=True)
def test_sort_projects(
    mta_app, create_minimal_project, create_project_with_two_apps, create_project
):
    """ Test to sort Projects

     Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create three different projects
            2. Go to project all page
            3. Sort projects by
                {"name" > "ascending" and "descending",
                 "Applications" > "ascending" and "descending",
                 "Status" > "ascending" and "descending"}
        expectedResults:
            1. All values should get sorted properly
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


@pytest.mark.parametrize("mta_app", ["ViaWebUI"], indirect=True)
def test_search_project(mta_app, create_minimal_project):
    """Test search Projects

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Create project
            2. Go to project all page and search by name
        expectedResults:
            1. Project with matching search value should appear
    """
    project, project_collection = create_minimal_project
    assert project.exists
    project_collection.search_project(project.name)
    view = project_collection.create_view(AllProjectView)
    assert project.name in [row.name.text for row in view.table]
