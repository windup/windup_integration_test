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


def test_advanced_options(mta_app, request):
    """ Test advanced options and run analysis

    Polarion:
        assignee: ghubale
        initialEstimate: 1/12h
        caseimportance: medium
        testSteps:
            1. Go to project all page and click on `Create project` button
            2. Add name and description and click on `Next`
            3. Select applications file and click on `Next`
            4. Select transformation target and click on `Next`
            5. Select packages and click on `Next`
            6. Add custom rule and click on `Next`
            7. Add custom label and click on `Next`
            8. Select all advanced options except `Skip reports` and click on `Next`
            9. Review project details and click on `Save and run`
            10. Go to analysis results page and click on show reports action button
        expectedResults:
            1. Analysis should be completed properly and new tab should open with detailed analysis
    """
    project_name = fauxfactory.gen_alphanumeric(12, start="project_")
    project_collection = mta_app.collections.projects
    view = navigate_to(project_collection, "Add")
    view.create_project.fill({"name": project_name, "description": "desc"})
    view.add_applications.wait_displayed("20s")

    app_list = ["acmeair-webapp-1.0-SNAPSHOT.war", "arit-ear-0.8.1-SNAPSHOT.ear"]
    env = conf.get_config("env")
    fs = FTPClientWrapper(env.ftpserver.entities.mta)
    for app in app_list:
        file_path = fs.download(app)
        view.add_applications.upload_file.fill(file_path)
        wait_for(
            lambda: view.browser.is_displayed(view.add_applications.progress_bar),
            delay=0.2,
            timeout=60,
        )

    view.add_applications.next_button.wait_displayed()
    wait_for(lambda: view.add_applications.next_button.is_enabled, delay=0.2, timeout=60)
    view.add_applications.next_button.click()

    view.configure_analysis.set_transformation_target.wait_displayed()
    view.configure_analysis.set_transformation_target.next_button.click()
    wait_for(
        lambda: view.configure_analysis.select_packages("com").is_displayed, delay=0.6, timeout=350
    )
    # Add package net and assert
    view.configure_analysis.select_packages("net").fill_pkg()
    view.configure_analysis.select_packages("com").wait_displayed("20s")
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
    # Issue with rule enabled. Uncomment once this issue resolved - WINDUP-3013
    # view.advanced.custom_rules.enabled_button.click()
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
    view.advanced.custom_labels.next_button.wait_displayed()
    view.advanced.custom_labels.next_button.click()
    view.advanced.options.wait_displayed("20s")

    # Add custom name to the application
    view.advanced.options.app_name.fill("custom_app_name")
    # select disable_tattletale and de-select it
    view.advanced.options.disable_tattletale.click()
    view.advanced.options.disable_tattletale.click()
    # select other options
    view.advanced.options.export_csv.click()
    view.advanced.options.class_not_found_analysis.click()
    view.advanced.options.compatible_files_report.click()
    view.advanced.options.exploded_app.click()
    view.advanced.options.keep_work_dirs.click()
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
    view.analysis_results.show_report(request)
    view = project_collection.create_view(AllApplicationsView)
    view.filter_application.wait_displayed("30s")
    assert view.is_displayed
    view.search("custom_app_name", "Name")
    view.wait_displayed("30s")
    apps_list = view.application_table.get_applications_list
    assert "custom_app_name" in apps_list[:-1]
