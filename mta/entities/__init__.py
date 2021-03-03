import attr
from wait_for import wait_for
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import PatternflyTable

from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.web_ui import navigate_to
from mta.base.application.implementations.web_ui import ViaWebUI
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

    def get_url(self):
        """The logged in Page in both web console and operator are same
        so added a url check to differentiate in the view"""
        url = (
            self.context["object"].application.ocphostname
            if self.context["object"].application.mta_context == "ViaOperatorUI"
            else self.context["object"].application.hostname
        )
        return url in self.context["object"].application.web_ui.widgetastic_browser.url

    @property
    def is_empty(self):
        """Check project is available or not; blank state"""
        return self.blank_state.is_displayed and self.get_url()

    @property
    def is_displayed(self):
        return self.header.is_displayed and self.help.is_displayed and self.get_url()


@attr.s
class BaseWebUICollection(BaseCollection):
    pass


class AllProjectView(BaseLoggedInPage):
    """This view represent Project All View"""

    title = Text(".//div[contains(@class, 'pf-c-content')]/h1")
    search = Input(locator=".//input[@aria-label='Filter by name']")
    sort = SortSelector("class", "btn btn-default dropdown-toggle")

    ACTIONS_INDEX = 4
    table = PatternflyTable(
        ".//table[contains(@class, 'pf-c-table pf-m-grid-md')]",
        column_widgets={
            "Name": Text(locator=".//a"),
            "Applications": Text(locator=".//td[@data-label='Applications']"),
            "Status": Text(locator=".//td[@data-label='Status']"),
            "Description": Text(locator=".//td[@data-label='Description']"),
            ACTIONS_INDEX: Dropdown(),
        },
    )

    create_project = Button("Create project")

    @View.nested
    class no_matches(View):  # noqa
        """After search if no match found"""

        text = Text(".//div[contains(@class, 'pf-c-empty-state__body')]")

    def clear_search(self):
        """Clear search"""
        if self.search.value:
            self.search.fill("")

    @property
    def all_projects(self):
        """Returns list of all project rows"""
        return [row for row in self.table]

    @property
    def is_displayed(self):
        return self.is_empty or (
            self.create_project.is_displayed and self.title.text == "Projects" and self.get_url()
        )

    def select_project(self, name):
        for row in self.table:
            if row.name.text == name:
                row.click()


class ProjectView(AllProjectView):
    project_dropdown = DropdownMenu(
        locator="//div[@class='pf-c-context-selector' or @class='pf-c-context-selector "
        "pf-m-expanded']"
    )

    def select_project_dropdown(self, project_name):
        self.project_dropdown.item_select(project_name)

    @property
    def is_displayed(self):
        return self.project_dropdown.is_displayed


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


@ViaWebUI.register_destination_for(BaseWebUICollection)
class LoggedIn(MTANavigateStep):
    VIEW = BaseLoggedInPage

    def prerequisite(self):
        if self.application.mta_context == "ViaOperatorUI":
            return navigate_to(self.obj, "OCPLoginScreen")

    def step(self):
        if self.application.mta_context == "ViaOperatorUI":
            self.prerequisite_view.login(self.application.user, self.application.password)
        else:
            self.application.web_ui.widgetastic_browser.url = self.application.hostname
        wait_for(lambda: self.view.is_displayed, timeout="30s")

    def resetter(self, *args, **kwargs):
        # If some views stuck while navigation; reset navigation by clicking logo
        self.view.header.click()


@ViaWebUI.register_destination_for(BaseWebUICollection)
class OCPLoginScreen(MTANavigateStep):
    VIEW = LoginPage

    def step(self):
        self.application.web_ui.widgetastic_browser.url = self.application.ocphostname
        wait_for(lambda: self.view.is_displayed, timeout="30s")
