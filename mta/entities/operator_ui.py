import attr
from taretto.navigate import NavigateToSibling
from wait_for import wait_for
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import PatternflyTable

from mta.base.application.implementations import MTAImplementationContext
from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.operator_ui import ViaOperatorUI
from mta.base.modeling import BaseCollection
from mta.widgetastic import DropdownMenu
from mta.widgetastic import Input
from mta.widgetastic import MTANavigation
from mta.widgetastic import SortSelector
from mta.entities import Server


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


@MTAImplementationContext.external_for(Server.logged_in, ViaOperatorUI)
class BaseOperatorUICollection(BaseCollection):
    pass


class LoginPage(View):
    username = Input(id='username')
    password = Input(id='password')
    login_button = Text(locator=".//div/input[@id='kc-login']")

    @property
    def is_displayed(self):
        return self.username.is_displayed and self.login_button.is_displayed

    def login(self):
        self.fill({
            'username': "mta",
            'password': "password",
        })
        self.login_button.click()


@MTAImplementationContext.external_for(Server.logged_in, ViaOperatorUI)
@ViaOperatorUI.register_destination_for(BaseOperatorUICollection)
class LoggedIn(MTANavigateStep):
    VIEW = BaseLoggedInPage
    prerequisite = NavigateToSibling('OCPLoginScreen')

    def step(self):
        self.prerequisite_view.login()
        wait_for(lambda: self.view.is_displayed, timeout="30s")


@ViaOperatorUI.register_destination_for(BaseOperatorUICollection)
class OCPLoginScreen(MTANavigateStep):
    VIEW = LoginPage

    def step(self):
        self.application.web_ui.widgetastic_browser.url = self.application.ocphostname
        wait_for(lambda: self.view.is_displayed, timeout="30s")
