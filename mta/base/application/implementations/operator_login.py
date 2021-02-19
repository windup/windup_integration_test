import attr
from taretto.navigate import NavigateToSibling
from wait_for import wait_for
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import PatternflyTable

from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.operator_ui import ViaOperatorWebUI
from mta.base.modeling import BaseCollection
from mta.widgetastic import DropdownMenu
from mta.widgetastic import Input
from mta.widgetastic import MTANavigation
from mta.widgetastic import SortSelector


class BlankStateView(View):
    """This view represent web-console without any project i.e. blank state"""

    ROOT = ".//div[contains(@class, 'pf-c-empty-state__content')]"

    title = Text(locator=".//h4")
    welcome_help = Text(locator=".//div[@class='welcome-help-text']")
    create_project = Button("Create project")
    documentation = Text(locator=".//a[contains(text(), 'documentation')]")

    @property
    def is_displayed(self):
        return (
            self.title.is_displayed
            and self.title.text == "Welcome to the Migration Toolkit for Applications"
            and self.create_project.is_displayed
        )


class BaseLoggedInPage(View):
    """This is base view for MTA"""

    header = Text(locator=".//img[@alt='brand']")
    navigation = MTANavigation(locator='//ul[@class="pf-c-nav__list"]')

    setting = DropdownMenu(
        locator=".//li[contains(@class, 'dropdown') and .//span[@class='pficon pficon-user']]"
    )
    help = Button(id="aboutButton")

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


class LoginPage(View):
    username = Input(id='inputUsername')
    password = Input(id='inputPassword')
    login = Button('Log In')


def login(self):
    username = "mta"
    password = "password"
    self.fill({
        'username': username,
        'password': password,
    })
    self.login.click()


@ViaOperatorWebUI.register_destination_for(BaseWebUICollection)
class LoggedIn(MTANavigateStep):
    VIEW = BaseLoggedInPage
    prerequisite = NavigateToSibling('LoginScreen')

    def step(self):
        self.application.operator_ui.widgetastic_browser.url = self.application.ocphostname
        wait_for(lambda: self.view.is_displayed, timeout="30s")
        with self.obj.appliance.context.use(ViaOperatorWebUI):
            self.obj.login()

    def resetter(self, *args, **kwargs):
        # If some views stuck while navigation; reset navigation by clicking logo
        self.view.header.click()


@ViaOperatorWebUI.register_destination_for(BaseWebUICollection)
class LoginScreen(MTANavigateStep):
    VIEW = LoginPage

    def prerequisite(self):
        ensure_browser_open(self.obj.appliance.server.address())

    def step(self, *args, **kwargs):
        ensure_browser_open(self.obj.appliance.server.address())
        if not self.view.is_displayed:
            raise Exception('Could not open the login screen')