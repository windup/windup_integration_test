from taretto.navigate import NavigateToAttribute
from taretto.navigate import NavigateToSibling
from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic_patternfly4 import Button

from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.web_ui import NavigatableMixin
from mta.base.application.implementations.web_ui import navigate_to
from mta.base.application.implementations.web_ui import ViaWebUI
from mta.entities import AllProjectView
from mta.entities import BaseLoggedInPage
from mta.entities import ProjectView
from mta.utils.update import Updateable
from mta.widgetastic import AnalysisResults
from mta.widgetastic import Input


class AnalysisResultsView(BaseLoggedInPage):

    run_analysis_button = Button("Run analysis")
    title = Text(locator=".//div/h1[normalize-space(.)='Analysis results']")
    search = Input("searchValue")
    close_search = Text(locator=".//span[@class='pficon pficon-close']")
    analysis_results = AnalysisResults()
    confirm_delete = Button("Yes")
    cancel_delete = Button("No")
    sort_analysis = Text(locator=".//th[contains(normalize-space(.), 'Analysis')]//i[1]")

    @property
    def is_displayed(self):
        return self.run_analysis_button.is_displayed and self.title.is_displayed

    def clear_search(self):
        """Clear search"""
        if self.search.value:
            self.close_search.click()

    @ParametrizedView.nested
    class analysis_row(ParametrizedView):  # noqa
        PARAMETERS = ("row",)

        analysis_number = Text(ParametrizedLocator(".//tr[{row}]//a[@class='pointer link']"))
        delete_analysis = Text(ParametrizedLocator(".//tr[{row}]//a[@title='Delete']//i"))

        @property
        def is_displayed(self):
            return self.delete_analysis.is_displayed and self.analysis_number.is_displayed


class AnalysisResults(Updateable, NavigatableMixin):
    """Analysis Configuration"""

    def __init__(self, application, project_name):
        self.application = application
        self.project_name = project_name

    def get_analysis_number(self, view, row):
        """ Method to return only digit from row text"""
        analysis_num = view.analysis_row(row).analysis_number.text
        only_digits = "".join([c for c in analysis_num if c.isdigit()])
        return only_digits

    def search_analysis(self, row):
        """ Search analysis results with analysis number
            Args:
            row: row number to search
        """
        view = navigate_to(self, "AnalysisResultsPage")
        view.search.fill(self.get_analysis_number(view, row))

    def run_analysis(self):
        """ Run analysis"""
        view = navigate_to(self, "AnalysisResultsPage")
        view.run_analysis_button.click()
        wait_for(lambda: view.analysis_results.in_progress(), delay=0.2, timeout=450)
        wait_for(lambda: view.analysis_results.is_analysis_complete(), delay=0.2, timeout=450)
        assert view.analysis_results.is_analysis_complete()

    def delete_analysis(self, row):
        """ Delete analysis results with analysis number
            Args:
            row: row number
        """
        view = navigate_to(self, "AnalysisResultsPage")
        view.analysis_row(row).delete_analysis.click()

    def sort_analysis(self):
        view = navigate_to(self, "AnalysisResultsPage")
        view.sort_analysis.click()


@ViaWebUI.register_destination_for(AnalysisResults)
class AllProject(MTANavigateStep):
    VIEW = AllProjectView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self):
        if not self.prerequisite_view.is_empty:
            self.prerequisite_view.navigation.select("Projects")


@ViaWebUI.register_destination_for(AnalysisResults)
class SelectProject(MTANavigateStep):
    VIEW = ProjectView
    prerequisite = NavigateToSibling("AllProject")

    def step(self):
        self.prerequisite_view.projects.select_project(self.obj.project_name)


@ViaWebUI.register_destination_for(AnalysisResults)
class AnalysisResultsPage(MTANavigateStep):
    prerequisite = NavigateToSibling("SelectProject")
    VIEW = AnalysisResultsView

    def step(self):
        self.prerequisite_view.navigation.select("Analysis Results")
