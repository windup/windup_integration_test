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
    project_collection = application.collections.projects
    view = navigate_to(project_collection, "Add")
    view.create_project.fill(
        {
            "name": fauxfactory.gen_alphanumeric(12, start="project_"),
            "description": fauxfactory.gen_alphanumeric(),
        }
    )
    view.add_applications.wait_displayed()
    env = conf.get_config("env")
    fs = FTPClientWrapper(env.ftpserver.entities.mta)
    file_path = fs.download("arit-ear-0.8.1-SNAPSHOT.ear")
    view.add_applications.upload_file.fill(file_path)
    file_path = fs.download("acmeair-webapp-1.0-SNAPSHOT.war")
    view.add_applications.upload_file.fill(file_path)
    view.add_applications.next_button.wait_displayed()
    wait_for(lambda: view.add_applications.next_button.is_enabled, delay=0.2, timeout=60)
    view.add_applications.next_button.click()
    view.configure_analysis.wait_displayed()
    wait_for(
        lambda: view.configure_analysis.application_packages.is_displayed, delay=0.6, timeout=240
    )

    view.configure_analysis.application_package("com").app_checkbox.click()
    assert not view.configure_analysis.application_package("com").include_pkg.is_displayed

    view.configure_analysis.application_package("org").app_checkbox.click()
    assert not view.configure_analysis.application_package("org").include_pkg.is_displayed
    assert view.configure_analysis.application_package("org").exclude_pkg.is_displayed

    view.configure_analysis.application_package("com").app_checkbox.click()
    view.configure_analysis.application_package("org").app_checkbox.click()

    # Select third party package and see if it is included
    # in include package and not in excluded package
    view.configure_analysis.application_package("javax").app_checkbox.click()
    assert view.configure_analysis.application_package("javax").include_pkg.is_displayed
    assert not view.configure_analysis.application_package("javax").exclude_pkg.is_displayed

    view.configure_analysis.application_package("javax").app_checkbox.click()
    assert not view.configure_analysis.application_package("javax").include_pkg.is_displayed
    assert view.configure_analysis.application_package("javax").exclude_pkg.is_displayed

    # Custom rules validation
    view.configure_analysis.use_custom_rules.expand_custom_rules.click()
    view.configure_analysis.use_custom_rules.add_button.click()
    # upload custom rules
    env = conf.get_config("env")
    fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
    file_path = fs1.download("custom.Test1rules.rhamt.xml")
    view.configure_analysis.use_custom_rules.upload_file.fill(file_path)
    view.configure_analysis.use_custom_rules.add_rules_button.wait_displayed()
    wait_for(
        lambda: view.configure_analysis.use_custom_rules.add_rules_button.is_enabled,
        delay=0.2,
        timeout=60,
    )
    view.configure_analysis.use_custom_rules.add_rules_button.click()
    view.configure_analysis.use_custom_rules.select_all_rules.click()
    assert view.configure_analysis.use_custom_rules.rule.is_displayed
    view.configure_analysis.use_custom_rules.expand_custom_rules.click()

    # Custom label validation
    view.configure_analysis.use_custom_labels.expand_custom_labels.click()
    view.configure_analysis.use_custom_labels.add_button.click()
    # upload custom label
    env = conf.get_config("env")
    fs2 = FTPClientWrapper(env.ftpserver.entities.mta)
    file_path = fs2.download("customWebLogic.windup.label.xml")
    view.configure_analysis.use_custom_labels.upload_file.fill(file_path)
    view.configure_analysis.use_custom_labels.add_labels_button.wait_displayed()
    wait_for(
        lambda: view.configure_analysis.use_custom_labels.add_labels_button.is_enabled,
        delay=0.2,
        timeout=60,
    )
    view.configure_analysis.use_custom_labels.add_labels_button.click()
    view.configure_analysis.use_custom_labels.select_all_labels.click()
    assert view.configure_analysis.use_custom_labels.label.is_displayed
    view.configure_analysis.use_custom_labels.expand_custom_labels.click()

    # advanced options
    view.configure_analysis.advanced_options.expand_advanced_options.click()
    view.configure_analysis.advanced_options.add_option_button.click()
    view.configure_analysis.advanced_options.option_select.fill("enableCompatibleFilesReport")
    view.configure_analysis.advanced_options.select_value.click()
    view.configure_analysis.advanced_options.cancel_button.click()

    view.configure_analysis.advanced_options.add_option_button.click()
    view.configure_analysis.advanced_options.option_select.fill("enableCompatibleFilesReport")
    view.configure_analysis.advanced_options.select_value.click()
    view.configure_analysis.advanced_options.add_button.click()
    # Delete added option
    view.configure_analysis.advanced_options.delete_button.click()
    # Add option and submit and run analysis
    view.configure_analysis.advanced_options.expand_advanced_options.click()
    view.configure_analysis.advanced_options.add_option_button.click()
    view.configure_analysis.advanced_options.option_select.fill("exportCSV")
    view.configure_analysis.advanced_options.select_value.click()
    view.configure_analysis.advanced_options.add_button.click()
    view.configure_analysis.save_and_run.click()
    # Verify that analysis completes
    view = project_collection.create_view(AnalysisResultsView)
    view.wait_displayed("60s")
    assert view.is_displayed
    wait_for(lambda: view.analysis_results.in_progress(), delay=0.6, timeout=450)
    wait_for(lambda: view.analysis_results.is_analysis_complete(), delay=0.2, timeout=450)
    assert view.analysis_results.is_analysis_complete()
    # Verify that report opens
    view.analysis_results.show_report()
    view = project_collection.create_view(AllApplicationsView)
    assert view.is_displayed
