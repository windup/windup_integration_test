from taretto.navigate import NavigateToAttribute
from taretto.navigate import NavigateToSibling
from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic_patternfly import Button
from widgetastic_patternfly import Input

from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.web_ui import NavigatableMixin
from mta.base.application.implementations.web_ui import navigate_to
from mta.base.application.implementations.web_ui import ViaWebUI
from mta.entities import AllProjectView
from mta.entities import BaseLoggedInPage
from mta.entities import ProjectView
from mta.entities.analysis_results import AnalysisResultsView
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper
from mta.utils.update import Updateable
from mta.widgetastic import HiddenFileInput


class ApplicationsView(BaseLoggedInPage):

    title = Text(locator=".//div/h2[normalize-space(.)='Applications']")
    add_application_button = Button("Add")
    upload_file = HiddenFileInput(id="fileUpload")
    search = Input("searchValue")
    close_search = Text(locator=".//span[@class='pficon pficon-close']")
    done_button = Button("Done")
    application_packages = Text(
        locator=".//wu-select-packages/h3[normalize-space(.)='Application packages']"
    )
    sort_application = Text(locator=".//th[contains(normalize-space(.), 'Application')]//i[1]")
    save_and_run_button = Button("Save & Run")
    yes_button = Button("Yes")
    no_button = Button("No")

    @property
    def is_displayed(self):
        return self.add_application_button.is_displayed and self.title.is_displayed

    def clear_search(self):
        """Clear search"""
        if self.search.value:
            self.close_search.click()

    @ParametrizedView.nested
    class application_row(ParametrizedView):  # noqa
        PARAMETERS = ("name",)

        application_name = Text(ParametrizedLocator(".//td[normalize-space(.)='{name}']"))
        delete_application = Text(
            ParametrizedLocator(
                ".//td[./preceding-sibling::td[normalize-space(.)='{name}']]"
                "/span/a[@title='Delete']//i"
            )
        )
        row = Text(ParametrizedLocator(".//tr[{name}]/td/a"))

        @property
        def is_displayed(self):
            return self.delete_application.is_displayed and self.application_name.is_displayed


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
        app = view.application_row(name).application_name.text
        view.search.fill(app)

    def delete_application(self, name, cancel=True):
        """ Delete application
        Args:
            name: name of app
        """
        view = navigate_to(self, "ApplicationsPage")
        view.application_row(name).delete_application.click()
        if cancel:
            view.no_button.is_displayed
            view.no_button.click()
        else:
            view.yes_button.click()

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
        wait_for(lambda: view.application_packages.is_displayed, delay=0.6, timeout=240)
        view.save_and_run_button.click()
        # wait for analysis to finish
        view = self.create_view(AnalysisResultsView, wait="30s")
        view.wait_displayed()
        assert view.is_displayed
        wait_for(lambda: view.analysis_results.in_progress(), delay=0.2, timeout=120)
        wait_for(lambda: view.analysis_results.is_analysis_complete(), delay=0.2, timeout=120)
        assert view.analysis_results.is_analysis_complete()

    def sort_application(self):
        view = navigate_to(self, "ApplicationsPage")
        view.sort_application.click()


@ViaWebUI.register_destination_for(Applications)
class AllProject(MTANavigateStep):
    VIEW = AllProjectView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self):
        if not self.prerequisite_view.is_empty:
            self.prerequisite_view.home_navigation.select("Projects")


@ViaWebUI.register_destination_for(Applications)
class SelectProject(MTANavigateStep):
    VIEW = ProjectView
    prerequisite = NavigateToSibling("AllProject")

    def step(self):
        self.prerequisite_view.projects.select_project(self.obj.project_name)


@ViaWebUI.register_destination_for(Applications)
class ApplicationsPage(MTANavigateStep):
    prerequisite = NavigateToSibling("SelectProject")
    VIEW = ApplicationsView

    def step(self):
        self.prerequisite_view.navigation.select("Applications")
