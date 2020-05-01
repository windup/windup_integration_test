from widgetastic.exceptions import NoSuchElementException
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic.widget import Widget
from widgetastic_patternfly import AggregateStatusCard
from widgetastic_patternfly import Dropdown
from widgetastic_patternfly import VerticalNavigation

from rhamt.utils.exceptions import ItemNotFound


class HOMENavigation(VerticalNavigation):
    """The Patternfly Vertical navigation for Home Icon (Projects)"""

    CURRENTLY_SELECTED = './/li[contains(@class, "home")]/a/span'


class RHAMTNavigation(VerticalNavigation):
    """The Patternfly Vertical navigation for left menu"""

    CURRENTLY_SELECTED = './/li[contains(@class, "active")]/a/span'


class ProjectSteps(AggregateStatusCard):
    ROOT = ParametrizedLocator(
        ".//ul[contains(@class, 'steps-container')]"
        "/li[contains(@class, 'steps active')]"
        "/span/a[contains(normalize-space(.),{@name|quote})]"
    )


class DropdownMenu(Dropdown):
    """This is custom dropdown menu; found at toolbar like
    HelpMenu and Configuration
    """

    ROOT = ParametrizedLocator("{@locator}")
    BUTTON_LOCATOR = ".//a[contains(@class, 'dropdown-toggle')]"

    def __init__(self, parent, locator, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.locator = locator


class TransformationPath(Widget):
    @ParametrizedView.nested
    class _card(ParametrizedView):
        PARAMETERS = ("card_name",)
        card = Text(
            ParametrizedLocator(
                './/div[contains(@class, "card-pf-view-multi-select")]'
                '/div[contains(@class, "card-pf-body")] '
                "/h2[contains(normalize-space(.),{card_name|quote})]"
            )
        )

        def click_card(self):
            """Clicks the list item with this name."""

            return self.card.click()

    def select_card(self, card_name):
        return self._card(card_name).click_card()


class SelectedApplications(Widget):
    @ParametrizedView.nested
    class _app(ParametrizedView):
        PARAMETERS = ("app_name",)
        delete_app_btn = Text(
            ParametrizedLocator(".//span[normalize-space(.)={app_name|quote}]/following-sibling::a")
        )

        def delete_app(self):
            """Clicks the close icon for the app."""

            return self.delete_app_btn.click()

    def delete_application(self, app_name):
        return self._app(app_name).delete_app()


class ProjectList(Widget):
    ROOT = ParametrizedLocator(".//div[contains(@class,'list-group list-view-pf projects-list')]")
    ITEM_LOCATOR = './div[contains(@class,"list-group-item")]'
    PROJECT_LOCATOR = './/div[contains(@class,"list-group-item-heading")]/a/h2'
    # TO DO implement delete and edit methods
    DELETE_PROJECT = './/a[@title="Delete project"]//i[1]'
    EDIT_PROJECT = './/a[@class="action-button action-edit-project"]//i[1]'

    def __init__(self, parent, locator, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.locator = locator

    @property
    def items(self):
        return [self.browser.text(item) for item in self.browser.elements(self.PROJECT_LOCATOR)]

    def read(self):
        return self.items

    def exists(self, project_name):
        return project_name in self.items

    def _get_project(self, project_name):
        for item in self.browser.elements(self.ITEM_LOCATOR):
            el = self.browser.element(
                ".//*[contains(@class,'list-group-item-heading')]/a/h2", parent=item
            )
            if self.browser.text(el) == project_name:
                return item
        raise ItemNotFound("Project: {} not found".format(project_name))

    def edit_project(self, project_name):
        try:
            el = self._get_project(project_name)
            self.browser.click(self.EDIT_PROJECT, parent=el)
            return True
        except NoSuchElementException:
            return False

    def delete_project(self, project_name):
        try:
            el = self._get_project(project_name)
            self.browser.click(self.DELETE_PROJECT, parent=el)
            return True
        except NoSuchElementException:
            return False


class AnalysisResults(Widget):
    SPINNER_LOCATOR = './/span[contains(@class, "status-icon")]/span[contains(@class,"spinner")]'
    COMPLETE_STATUS_LOCATOR = './/span[contains(@class, "fa fa-check")]'
    SHOW_REPORT = './/i[contains(@class,"fa fa-bar-chart")]'

    def in_progress(self):
        return self.browser.is_displayed(self.SPINNER_LOCATOR)

    def is_analysis_complete(self):
        """Returns True if analysis complete and spinner not present"""
        return self.browser.is_displayed(self.COMPLETE_STATUS_LOCATOR)

    def show_report(self):
        self.browser.click(self.SHOW_REPORT)
        self.switch_to_report()

    def switch_to_report(self):
        """Switch focus to report window."""
        main_window = self.browser.current_window_handle
        open_url_window = (set(self.browser.window_handles) - {main_window}).pop()
        self.browser.switch_to_window(open_url_window)
