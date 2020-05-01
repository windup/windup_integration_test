import attr
from wait_for import wait_for
from widgetastic.widget import Text
from widgetastic.widget import View

from rhamt.base.application.implementations.web_ui import RhamtNavigateStep
from rhamt.base.application.implementations.web_ui import ViaWebUI
from rhamt.base.modeling import BaseCollection
from rhamt.widgetastic import DropdownMenu
from rhamt.widgetastic import HOMENavigation
from rhamt.widgetastic import RHAMTNavigation


class BaseLoggedInPage(View):
    header = Text(locator=".//span[@id='header-logo']")
    home_navigation = HOMENavigation("//ul")
    navigation = RHAMTNavigation('//ul[@class="list-group"]')

    setting = DropdownMenu(
        locator=".//li[contains(@class, 'dropdown') and .//span[@class='pficon pficon-user']]"
    )
    help = DropdownMenu(
        locator=".//li[contains(@class, 'dropdown') and .//span[@class='pficon pficon-help']]"
    )

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
