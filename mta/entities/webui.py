from wait_for import wait_for

from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.web_ui import ViaWebUI
from mta.entities import BaseLoggedInPage
from mta.entities import BaseWebUICollection


@ViaWebUI.register_destination_for(BaseWebUICollection)
class LoggedIn(MTANavigateStep):
    VIEW = BaseLoggedInPage

    def step(self):
        self.application.web_ui.widgetastic_browser.url = self.application.hostname
        wait_for(lambda: self.view.is_displayed, timeout="30s")

    def resetter(self, *args, **kwargs):
        # If some views stuck while navigation; reset navigation by clicking logo
        self.view.header.click()
