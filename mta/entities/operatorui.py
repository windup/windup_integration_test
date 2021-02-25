from navmazing import NavigateToSibling
from wait_for import wait_for
from widgetastic.widget import Text
from widgetastic.widget import View

from mta.base.application.implementations.operator_ui import MTANavigateStep
from mta.base.application.implementations.operator_ui import ViaOperatorUI
from mta.entities import BaseLoggedInPage
from mta.entities import BaseWebUICollection
from mta.widgetastic import Input


class LoginPage(View):
    username = Input(id="username")
    password = Input(id="password")
    login_button = Text(locator=".//div/input[@id='kc-login']")

    @property
    def is_displayed(self):
        return self.username.is_displayed and self.login_button.is_displayed

    def login(self, user, password):
        self.fill({"username": user, "password": password})
        self.login_button.click()


@ViaOperatorUI.register_destination_for(BaseWebUICollection)
class LoggedIn(MTANavigateStep):
    VIEW = BaseLoggedInPage
    prerequisite = NavigateToSibling("OCPLoginScreen")

    def step(self):
        self.prerequisite_view.login(self.application.user, self.application.password)
        wait_for(lambda: self.view.is_displayed, timeout="30s")


@ViaOperatorUI.register_destination_for(BaseWebUICollection)
class OCPLoginScreen(MTANavigateStep):
    VIEW = LoginPage

    def step(self):
        self.application.operator_ui.widgetastic_browser.url = self.application.ocphostname
        wait_for(lambda: self.view.is_displayed, timeout="30s")
