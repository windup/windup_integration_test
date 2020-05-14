import attr
from wait_for import wait_for
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly import Button

from rhamt.base.application.implementations.web_ui import RhamtNavigateStep
from rhamt.base.application.implementations.web_ui import ViaWebUI
from rhamt.base.modeling import BaseCollection
from rhamt.widgetastic import DropdownMenu
from rhamt.widgetastic import HOMENavigation
from rhamt.widgetastic import RHAMTNavigation


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
    """This is base view for RHAMT"""

    header = Text(locator=".//span[@id='header-logo']")
    home_navigation = HOMENavigation("//ul")
    navigation = RHAMTNavigation('//ul[@class="list-group"]')

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
        return (
            "RED HAT APPLICATION MIGRATION TOOLKIT" in self.header.text
            and self.header.is_displayed
            and self.help.is_displayed
        )


@attr.s
class BaseWebUICollection(BaseCollection):
    pass


@ViaWebUI.register_destination_for(BaseWebUICollection)
class LoggedIn(RhamtNavigateStep):
    VIEW = BaseLoggedInPage

    def step(self):
        self.application.web_ui.widgetastic_browser.url = self.application.hostname
        wait_for(lambda: self.view.is_displayed, timeout="30s")

    def resetter(self, *args, **kwargs):
        # If some views stuck while navigation; reset navigation by clicking logo
        self.view.header.click()
