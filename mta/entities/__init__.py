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
            and self.title.text == "Welcome to Windup"
            and self.create_project.is_displayed
        )


class BaseLoggedInPage(View):
    """This is base view for MTA"""

    header = Text(locator=".//img[@alt='brand']")
    navigation = MTANavigation(locator='//ul[@class="pf-c-nav__list"]')
    logout_button = Dropdown(text="mta")

    setting = DropdownMenu(
        locator=".//li[contains(@class, 'dropdown') and .//span[@class='pficon pficon-user']]"
    )
    help = Button(id="aboutButton")

    # only if no project available
    blank_state = View.nested(BlankStateView)

    def validate_url(self):
        """The logged in Page in both web console and operator are same
        so added a url check to differentiate in the view"""
        if self.context["object"].application.mta_context == "ViaOperatorUI":
            url = self.context["object"].application.ocphostname
        elif self.context["object"].application.mta_context == "ViaSecure":
            url = self.context["object"].application.ocpsecurehostname
        elif self.context["object"].application.mta_context == "ViaWebUI":
            url = self.context["object"].application.hostname
        return url in self.context["object"].application.web_ui.widgetastic_browser.url

    @property
    def is_empty(self):
        """Check project is available or not; blank state"""
        return self.blank_state.is_displayed and self.validate_url()

    @property
    def is_displayed(self):
        return self.header.is_displayed and self.help.is_displayed and self.validate_url()

    def logout(self):
        self.logout_button.item_select("Logout")


@attr.s
class BaseWebUICollection(BaseCollection):
    pass


class AllProjectView(BaseLoggedInPage):
    """This view represent Project All View"""

    title = Text(".//div[contains(@class, 'pf-c-content')]/h1")
    search = Input(locator=".//input[@aria-label='Filter by name']")
    sort = SortSelector("class", "btn btn-default dropdown-toggle")
    table_loading = './/div[contains(@class, "pf-c-skeleton")]'

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
            self.create_project.is_displayed
            and self.title.text == "Projects"
            and self.table.is_displayed
            and self.validate_url()
        )

    def select_project(self, name):
        for row in self.table:
            if row.name.text == name:
                row["Name"].widget.click()

    def table_loaded(self):
        return wait_for(
            lambda: not self.browser.is_displayed(self.table_loading), delay=10, timeout=120
        )


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
    header = Text(locator=".//img[@alt='brand']")
    logout_button = Dropdown(text="mta")

    def validate_url(self):
        """The logged in Page in both web console and operator are same
        so added a url check to differentiate in the view"""
        if self.context["object"].application.mta_context == "ViaOperatorUI":
            url = self.context["object"].application.ocphostname
        elif self.context["object"].application.mta_context == "ViaSecure":
            url = self.context["object"].application.ocpsecurehostname
        elif self.context["object"].application.mta_context == "ViaWebUI":
            url = self.context["object"].application.hostname
        return url in self.context["object"].application.web_ui.widgetastic_browser.url

    @property
    def is_displayed(self):
        return (
            self.username.is_displayed and self.login_button.is_displayed and self.validate_url()
        ) or (self.validate_url() and self.header.is_displayed)

    def login(self, user, password):
        self.fill({"username": user, "password": password})
        self.login_button.click()


@ViaWebUI.register_destination_for(BaseWebUICollection)
class LoggedIn(MTANavigateStep):
    VIEW = BaseLoggedInPage

    def prerequisite(self):
        if self.application.mta_context != "ViaWebUI":
            return navigate_to(self.obj, "OCPLoginScreen")

    def step(self):
        if self.application.mta_context == "ViaWebUI":
            self.application.web_ui.widgetastic_browser.url = self.application.hostname
        else:
            self.prerequisite_view.login(self.application.user, self.application.password)
        wait_for(lambda: self.view.is_displayed, timeout="30s")

    def resetter(self, *args, **kwargs):
        # If some views stuck while navigation; reset navigation by clicking logo
        self.view.header.click()
        self.view.wait_displayed("30s")


@ViaWebUI.register_destination_for(BaseWebUICollection)
class OCPLoginScreen(MTANavigateStep):
    VIEW = LoginPage

    def step(self):
        if self.application.mta_context == "ViaOperatorUI":
            self.application.web_ui.widgetastic_browser.url = self.application.ocphostname
        elif self.application.mta_context == "ViaSecure":
            self.application.web_ui.widgetastic_browser.url = self.application.ocpsecurehostname
        wait_for(lambda: self.view.is_displayed, timeout="30s")
