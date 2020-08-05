import attr
from wait_for import wait_for
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly import Button
from widgetastic_patternfly import Input

from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.web_ui import ViaWebUI
from mta.base.modeling import BaseCollection
from mta.widgetastic import DropdownMenu
from mta.widgetastic import HOMENavigation
from mta.widgetastic import MTANavigation
from mta.widgetastic import ProjectList


class BlankStateView(View):
    """This view represent web-console without any project i.e. blank state"""

    ROOT = ".//div[contains(@class, 'blank-slate')]"

    title = Text(locator=".//h1")
    welcome_help = Text(locator=".//div[@class='welcome-help-text']")
    new_project_button = Button("New Project")
    documentation = Text(locator=".//a[contains(text(), 'documentation')]")

    @property
    def is_displayed(self):
        return (
            self.title.is_displayed
            and self.title.text == "Welcome to the Web Console."
            and self.new_project_button.is_displayed
        )


class BaseLoggedInPage(View):
    """This is base view for MTA"""

    header = Text(locator=".//img[@id='header-logo']")
    home_navigation = HOMENavigation("//ul")
    navigation = MTANavigation('//ul[@class="list-group"]')

    setting = DropdownMenu(
        locator=".//li[contains(@class, 'dropdown') and .//span[@class='pficon pficon-user']]"
    )
    help = DropdownMenu(
        locator=".//li[contains(@class, 'dropdown') and .//span[@class='pficon pficon-help']]"
    )

    # only if no project available
    blank_state = View.nested(BlankStateView)

    @property
    def is_empty(self):
        """Check project is available or not; blank state"""
        return self.blank_state.is_displayed

    @property
    def is_displayed(self):
        return self.header.is_displayed and self.help.is_displayed


@attr.s
class BaseWebUICollection(BaseCollection):
    pass


class AllProjectView(BaseLoggedInPage):
    """This view represent Project All View"""

    title = Text(".//div[contains(@class, 'projects-bar')]/h1")
    search = Input(".//input[contains(@name, 'searchValue')]")
    # TODO: add custom sort widget

    projects = ProjectList(locator=".//div[contains(@class, 'projects-list')]")
    new_project_button = Button("New Project")

    @View.nested
    class no_matches(View):  # noqa
        """After search if no match found"""

        text = Text(".//div[contains(@class, 'no-matches')]")
        remove = Text(".//div[contains(@class, 'no-matches')]/a")

    def clear_search(self):
        """Clear search"""
        if self.search.value:
            self.search.fill("")

    @property
    def is_displayed(self):
        return self.is_empty or (
            self.new_project_button.is_displayed and self.title.text == "Projects"
        )


class ProjectView(AllProjectView):
    project_dropdown = DropdownMenu(
        locator=".//li[contains(@class, 'dropdown') and .//span[@class='nav-item']]"
    )

    @property
    def is_displayed(self):
        return self.project_dropdown.is_displayed


@ViaWebUI.register_destination_for(BaseWebUICollection)
class LoggedIn(MTANavigateStep):
    VIEW = BaseLoggedInPage

    def step(self):
        self.application.web_ui.widgetastic_browser.url = self.application.hostname
        wait_for(lambda: self.view.is_displayed, timeout="30s")

    def resetter(self, *args, **kwargs):
        # If some views stuck while navigation; reset navigation by clicking logo
        self.view.header.click()
