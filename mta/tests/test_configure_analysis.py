import fauxfactory
from wait_for import wait_for

from mta.base.application.implementations.web_ui import navigate_to
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper


def test_packages_include_exclude(application):
    """Test java packages to include/exclude in the analysis"""
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = application.collections.projects
    view = navigate_to(project_collection, "Add")
    view.create_project.fill({"name": project_name, "description": "desc"})
    view.add_applications.wait_displayed("20s")
    env = conf.get_config("env")
    fs = FTPClientWrapper(env.ftpserver.entities.mta)
    file_path = fs.download("arit-ear-0.8.1-SNAPSHOT.ear")
    view.add_applications.upload_file.fill(file_path)
    file_path = fs.download("acmeair-webapp-1.0-SNAPSHOT.war")
    view.add_applications.upload_file.fill(file_path)
    view.add_applications.next_button.wait_displayed()
    wait_for(lambda: view.add_applications.next_button.is_enabled, delay=0.2, timeout=60)
    view.add_applications.next_button.click()
    view.configure_analysis.set_transformation_target.wait_displayed()
    view.configure_analysis.set_transformation_target.next_button.click()
    view.configure_analysis.select_packages("net").all_packages.click()
    view.configure_analysis.select_packages("pkg").include.click()
    assert view.configure_analysis.select_packages("net").included_packages.is_displayed
