from taretto.navigate import NavigateToAttribute
from taretto.navigate import NavigateToSibling
from wait_for import wait_for
from widgetastic.widget import Text
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import PatternflyTable

from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.web_ui import NavigatableMixin
from mta.base.application.implementations.web_ui import navigate_to
from mta.base.application.implementations.web_ui import ViaWebUI
from mta.entities import AllProjectView
from mta.entities import BaseLoggedInPage
from mta.entities import ProjectView
from mta.entities.analysis_configuration import AnalysisConfiguration
from mta.entities.analysis_results import AnalysisResultsView
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper
from mta.utils.update import Updateable
from mta.widgetastic import HiddenFileInput
from mta.widgetastic import Input


class ApplicationsView(BaseLoggedInPage):

    title = Text(locator=".//div/h2[normalize-space(.)='Applications']")
    ACTIONS_INDEX = 2
    table = PatternflyTable(
        ".//table[contains(@class, 'pf-c-table')]",
        column_widgets={
            "Application": Text(locator=".//a"),
            "Date added": Text(locator=".//td[@data-label='Date added']"),
            ACTIONS_INDEX: Dropdown(),
        },
    )
    add_application_button = Button("Add application")
    upload_file = HiddenFileInput(locator='.//input[@accept=".ear,.har,.jar,.rar,.sar,.war,.zip"]')
    search = Input(locator=".//input[@aria-label='Filter by name']")
    done_button = Button("Close")
    application_packages = Text(
        locator=".//wu-select-packages/h3[normalize-space(.)='Application packages']"
    )
    sort_application = Text(locator=".//th[contains(normalize-space(.), 'Application')]//i[1]")
    save_and_run_button = Button("Save and run")
    delete_button = Button("Delete")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.add_application_button.is_displayed and self.title.is_displayed

    def clear_search(self):
        """Clear search"""
        if self.search.value:
            self.search.fill("")


class Applications(Updateable, NavigatableMixin):
    """Analysis Configuration"""

    def __init__(self, application, project_name):
        self.application = application
        self.project_name = project_name

    def search_application(self, name):
        """ Search application
        Args:
            name: name to search
        """
        view = navigate_to(self, "ApplicationsPage")
        view.search.fill(name)

    def delete_application(self, name, cancel=True):
        """ Delete application
        Args:
            name: name of app
        """
        view = navigate_to(self, "ApplicationsPage")
        for row in view.table:
            if row.application.text == name:
                row[view.ACTIONS_INDEX].widget.item_select("Delete")
        if cancel:
            view.cancel_button.click()
        else:
            view.delete_button.click()

    def add_application(self, app):
        """ Add application
        Args:
            app: name of app
        """
        view = navigate_to(self, "ApplicationsPage")
        view.add_application_button.click()
        env = conf.get_config("env")
        fs = FTPClientWrapper(env.ftpserver.entities.mta)
        # Download application file to analyze
        file_path = fs.download(app)
        view.upload_file.fill(file_path)
        view.done_button.click()
        # Save Configuration
        view = navigate_to(self, "AllProject")
        analysis_configuration = AnalysisConfiguration(self.application, self.project_name)
        analysis_configuration.save_and_run_configuration()
        # wait for analysis to finish
        view = self.create_view(AnalysisResultsView)
        view.wait_displayed("60s")
        assert view.is_displayed
        wait_for(lambda: view.analysis_results.in_progress(), delay=0.2, timeout=450)
        wait_for(lambda: view.analysis_results.is_analysis_complete(), delay=0.2, timeout=450)
        assert view.analysis_results.is_analysis_complete()

    def sort_application(self, criteria, order):
        view = navigate_to(self, "ApplicationsPage")
        view.table.sort_by(criteria, order)


@ViaWebUI.register_destination_for(Applications)
class AllProject(MTANavigateStep):
    VIEW = AllProjectView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self):
        if not self.prerequisite_view.is_empty:
            self.prerequisite_view.navigation.select("Projects")


@ViaWebUI.register_destination_for(Applications)
class SelectProject(MTANavigateStep):
    VIEW = ProjectView
    prerequisite = NavigateToSibling("AllProject")

    def step(self):
        self.prerequisite_view.select_project(self.obj.project_name)


@ViaWebUI.register_destination_for(Applications)
class ApplicationsPage(MTANavigateStep):
    prerequisite = NavigateToSibling("SelectProject")
    VIEW = ApplicationsView

    def step(self):
        self.prerequisite_view.navigation.select("Applications")
