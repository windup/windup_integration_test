from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from wait_for import wait_for
from widgetastic.exceptions import DoNotReadThisWidget
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import FileInput
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic.widget import Widget
from widgetastic_patternfly import AggregateStatusCard
from widgetastic_patternfly import Button
from widgetastic_patternfly import Input
from widgetastic_patternfly import SelectorDropdown
from widgetastic_patternfly4 import CheckboxSelect
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import Navigation
from widgetastic_patternfly4 import Select
from widgetastic_patternfly4 import Tab


class MTANavigation(Navigation):
    """The Patternfly 4 navigation for left menu"""

    ITEM_MATCHING = "//li/a[contains(normalize-space(.), {})]"


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
    BUTTON_LOCATOR = (
        ".//span[@class='filter-by']/parent::button | "
        ".//span[@id='sort-by']/parent::button | "
        ".//button[contains(@class, 'pf-c-context-selector__toggle')] | "
        ".//span[@class='pf-c-select__toggle-icon']/parent::div/parent::button"
    )
    ITEMS_LOCATOR = ".//ul/li/button | .//ul/li/a"
    ITEM_LOCATOR = ".//ul/li/button | .//ul/li/a[normalize-space(.)={}]"

    def __init__(self, parent, locator, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.locator = locator

    @property
    def is_open(self):
        """Returns True if the Dropdown is open"""
        all_classes = self.browser.classes(self)
        return "open" in all_classes or "pf-m-expanded" in all_classes


class MTACheckboxSelect(CheckboxSelect):
    """Represents the custom Patternfly Select."""

    BUTTON_LOCATOR = (
        ".//span[@class='pf-c-select__toggle-arrow']/parent::button["
        "contains(@aria-labelledby, 'Filter by Source')] |"
        ".//span[@class='pf-c-select__toggle-arrow']/parent::button["
        "contains(@aria-labelledby, 'Filter by Target')]"
    )


class SortSelector(SelectorDropdown):
    def item_select(self, item, *args, **kwargs):
        super(SelectorDropdown, self).item_select(item, *args, **kwargs)
        wait_for(lambda: self.currently_selected.lower() == item.lower(), num_sec=3, delay=0.2)


class MTASelect(Select):
    """Select for MTA"""

    BUTTON_LOCATOR = ".//button[contains(@class, 'pf-c-select__toggle-button')]"


class TransformationPathSelect(Select):
    """Select for MTA"""

    BUTTON_LOCATOR = ".//button[contains(@class, 'pf-c-select__toggle')]"


class TransformationPath(Widget):
    ROOT = './/div[contains(@class,"pf-c-empty-state__content")]'

    @ParametrizedView.nested
    class _card(ParametrizedView):
        PARAMETERS = ("card_name",)
        card = Text(ParametrizedLocator("//h4[contains(normalize-space(.), {card_name|quote})]"))
        select_eap = TransformationPathSelect(locator='.//div[contains(@class, "pf-c-select")]')

        def click_card(self):
            """Clicks the card with this name."""
            return self.card.click()

        def read(self):
            """Reads the card with this name."""
            return self.select_eap.read()

    def select_card(self, card_name):
        return self._card(card_name).click_card()

    def read_card(self, card_name):
        return self._card(card_name).read()


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


class AnalysisResults(Widget):
    # When there are multiple analysis the first row is latest one
    # so we need to check spinner and success in 1st row

    COMPLETE_STATUS_LOCATOR = './/tr[1]/td[@data-label="Status"]/span[text()="Completed"]'
    SHOW_REPORT = './/a[@title="Reports"]'
    PROGRESS_BAR = './/div[contains(@role, "progressbar")]'

    def in_progress(self):
        return self.browser.is_displayed(self.PROGRESS_BAR)

    def is_analysis_complete(self):
        """Returns True if analysis complete and spinner not present"""
        return not self.browser.is_displayed(self.PROGRESS_BAR) and self.browser.is_displayed(
            self.COMPLETE_STATUS_LOCATOR
        )

    def show_report(self, request):
        self.browser.click(self.SHOW_REPORT)
        self.switch_to_report(request)

    def switch_to_report(self, request):
        """Switch focus to report window."""

        @request.addfinalizer
        def _finalize():
            self.browser.selenium.close()
            self.browser.switch_to_window(main_window)

        main_window = self.browser.current_window_handle
        open_url_window = (set(self.browser.window_handles) - {main_window}).pop()
        self.browser.switch_to_window(open_url_window)


class HiddenFileInput(FileInput):
    """Uploads file via hidden input form field

    Prerequisite:
        Type of input field should be file (type='file')
    """

    @property
    def is_displayed(self):
        self.browser.set_attribute("style", "display: none;", self)
        return self.browser.is_displayed(self)


class AddButton(Button):
    """Multiple buttons with same name are present in UI.
       So need to specify the locator.
    """

    def __locator__(self):
        return ".//button[text()='Cancel']/following-sibling::button"


class Input(Input):
    """Customized fill method for Input widget."""

    def fill(self, value):
        current_value = self.value
        if value == current_value:
            return False
        # Clear and type everything
        self.browser.click(self)
        self.browser.send_keys(f"{Keys.CONTROL}+a,{Keys.DELETE}", self)
        self.browser.send_keys(value, self)
        return True


class FilterInput(Input):
    """Customized filter Input widget."""

    def fill(self, value):
        current_value = self.value
        if value == current_value:
            return False
        # Clear and type everything
        self.browser.click(self)
        self.browser.send_keys(f"{Keys.CONTROL}+a,{Keys.DELETE}", self)
        self.browser.send_keys(value, self)
        self.browser.send_keys(Keys.ENTER, self)
        return True


class ApplicationList(Widget):
    """Application list widget."""

    APP_ITEMS_LOCATOR = './/div[contains(@class, "fileName")]/a'

    @property
    def get_applications_list(self):
        """Returns list of applications by name"""
        result = [self.browser.text(el) for el in self.browser.elements(self.APP_ITEMS_LOCATOR)]
        return result

    def application_details(self, app_name):
        """Clicks on specific application to navigate to it's details page"""
        all_apps = self.browser.elements(self.APP_ITEMS_LOCATOR)
        for el in all_apps:
            if self.browser.text(el) == app_name:
                self.browser.click(el)


class MTATab(Tab):
    """Represents the custom Patternfly Tab widget."""

    # Locator of the Tab selector
    TAB_LOCATOR = ParametrizedLocator(
        './/div[contains(@class, "pf-c-tabs")]/ul'
        "//li[button[normalize-space(.)={@tab_name|quote}]] | "
        ".//ul[contains(@class, 'nav')]/li[./a[normalize-space(.)={@tab_name|quote}]] |"
        ".//ul[contains(@class, 'pf-c-tabs__list')]/li["
        "./button[normalize-space(.)={@tab_name|quote}]]"
    )

    def is_active(self):
        """Returns a boolean detailing of the tab is active."""
        return "pf-m-current" or "pf-c-tabs__item" in self.parent_browser.classes(self.TAB_LOCATOR)


class Card(View):
    """
    Represents a generic patternfly 4 card

    This can eventually reside in the wt.pf4 repo
    """

    ROOT = ParametrizedLocator("{@locator}")

    header = Text('./div[contains(@class, "pf-c-card__header")]')
    body = Text('./div[contains(@class, "pf-c-card__body")]')
    footer = Text('./div[contains(@class, "pf-c-card__footer")]')
    expand_card = Text(".//button")

    def __init__(self, parent, locator=None, logger=None):
        super().__init__(parent, logger=logger)
        if not locator:
            self.locator = './/article[contains(@class, "pf-c-card")]'
        else:
            self.locator = locator

    def open(self):
        if not self.body.is_displayed:
            self.expand_card.click()

    def read(self):
        self.open()
        result = {}
        for widget_name in self.widget_names:
            widget = getattr(self, widget_name)
            try:
                value = widget.read()
            except (NotImplementedError, NoSuchElementException, DoNotReadThisWidget):
                continue

            result[widget_name] = value

        return result

    @property
    def is_displayed(self):
        return self.header.is_displayed
