import fauxfactory
from wait_for import wait_for

from mta.base.application.implementations.web_ui import navigate_to
from mta.entities.analysis_results import AnalysisResultsView
from mta.entities.report import AllApplicationsView
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper


def test_advanced_options(application):
    """ Validates Web console Test 06
    1) Select advanced options in analysis configuration page
    2) Upload custom rules
    2) Upload custom label
    3) Select advanced options like "enablecompatiblefile"
    4) Run analysis
    5) Open Report
    """
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
    wait_for(
        lambda: view.configure_analysis.select_packages("com").is_displayed, delay=0.6, timeout=240
    )
    # Add package net and assert
    view.configure_analysis.select_packages("net").fill_pkg()
    assert view.configure_analysis.select_packages("net").included_packages.is_displayed
    assert not view.configure_analysis.select_packages("net").packages.is_displayed
    # Add package 'org' and assert
    view.configure_analysis.select_packages("org").fill_pkg()
    assert view.configure_analysis.select_packages("org").included_packages.is_displayed
    assert not view.configure_analysis.select_packages("org").packages.is_displayed
    # Remove package 'org' and assert
    view.configure_analysis.select_packages("org").remove()
    assert not view.configure_analysis.select_packages("org").included_packages.is_displayed
    assert view.configure_analysis.select_packages("org").packages.is_displayed
    # Remove  package 'net' and assert
    view.configure_analysis.select_packages("net").remove()
    assert not view.configure_analysis.select_packages("net").included_packages.is_displayed
    assert view.configure_analysis.select_packages("net").packages.is_displayed
    view.configure_analysis.select_packages("net").next_button.click()

    view.advanced.custom_rules.wait_displayed()
    view.advanced.custom_rules.add_rule_button.click()
    # upload custom rules
    env = conf.get_config("env")
    fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
    file_path = fs1.download("custom.Test1rules.rhamt.xml")
    view.advanced.custom_rules.upload_rule.fill(file_path)
    view.advanced.custom_rules.close_button.click()
    view.advanced.custom_rules.enabled_button.wait_displayed()
    view.advanced.custom_rules.enabled_button.click()
    view.advanced.custom_rules.next_button.click()

    view.advanced.custom_labels.wait_displayed()
    view.advanced.custom_labels.add_label_button.click()
    # upload custom rules
    env = conf.get_config("env")
    fs2 = FTPClientWrapper(env.ftpserver.entities.mta)
    file_path = fs2.download("customWebLogic.windup.label.xml")
    view.advanced.custom_labels.upload_label.fill(file_path)
    view.advanced.custom_labels.close_button.click()
    view.advanced.custom_labels.enabled_button.wait_displayed()
    view.advanced.custom_labels.enabled_button.click()
    view.advanced.custom_labels.next_button.click()
    view.advanced.options.wait_displayed()
    # select disable_tattletale and de-select it
    view.advanced.options.disable_tattletale.click()
    view.advanced.options.disable_tattletale.click()
    # select other options
    view.advanced.options.export_csv.click()
    view.advanced.options.class_not_found_analysis.click()
    view.advanced.options.compatible_files_report.click()
    view.advanced.options.exploded_app.click()
    view.advanced.options.keep_work_dirs.click()
    view.advanced.options.skip_reports.click()
    view.advanced.options.allow_network_access.click()
    view.advanced.options.mavenize.click()
    view.advanced.options.source_mode.click()

    view.advanced.options.select_target.item_select("cloud-readiness")
    view.advanced.options.next_button.click()
    view.review.wait_displayed()
    view.review.save_and_run.click()
    # Verify that analysis completes
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed()
    assert view.is_displayed
    wait_for(lambda: view.analysis_results.in_progress(), delay=0.2, timeout=450)
    wait_for(lambda: view.analysis_results.is_analysis_complete(), delay=0.2, timeout=450)
    assert view.analysis_results.is_analysis_complete()

    # Verify that report opens
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    assert view.is_displayed
