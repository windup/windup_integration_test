from taretto.navigate import NavigateToAttribute
from widgetastic.widget import Text
from widgetastic_patternfly import Button

from rhamt.base.application.implementations.web_ui import NavigatableMixin
from rhamt.base.application.implementations.web_ui import navigate_to
from rhamt.base.application.implementations.web_ui import RhamtNavigateStep
from rhamt.base.application.implementations.web_ui import ViaWebUI
from rhamt.entities import BaseLoggedInPage
from rhamt.utils.update import Updateable
from rhamt.widgetastic import SelectedApplications
from rhamt.widgetastic import TransformationPath


class AnalysisConfigurationView(BaseLoggedInPage):

    save_and_run_button = Button("Save & Run")
    title = Text(locator=".//div/h2[normalize-space(.)='Analysis Configuration']")
    transformation_path = TransformationPath()
    selected_applications = SelectedApplications()
    select_none = Button("Select None")
    select_app_msg = Text(
        locator=".//span[normalize-space(.)= "
        "'You must select an application to run the analysis with')]"
    )

    @property
    def is_displayed(self):
        return self.transformation_path.is_displayed and self.title.is_displayed


class AnalysisConfiguration(Updateable, NavigatableMixin):
    """Analysis Configuration"""

    def __init__(self, application):
        self.application = application

    def delete_application(self, app_name):
        """ Delete application to be analysed
        Args:
            app_name: Application
        """
        view = navigate_to(self, "AnalysisConfigurationPage")
        view.selected_applications.delete_application(app_name)
        view.save_and_run_button.click()

    def select_none(self):
        """ Delete all application to be analysed
        Args:
            app_name: Application
        """
        view = navigate_to(self, "AnalysisConfiguration")
        view.select_none.click()
        assert view.select_app_msg.is_displayed()


@ViaWebUI.register_destination_for(AnalysisConfiguration)
class AnalysisConfigurationPage(RhamtNavigateStep):
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")
    VIEW = AnalysisConfigurationView

    def step(self):
        self.prerequisite_view.navigation.select("Analysis Configuration")
