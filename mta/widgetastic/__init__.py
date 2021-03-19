from selenium.webdriver.common.keys import Keys
from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import FileInput
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic.widget import Widget
from widgetastic_patternfly import AggregateStatusCard
from widgetastic_patternfly import Button
from widgetastic_patternfly import Input
from widgetastic_patternfly import SelectorDropdown
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import Navigation
from widgetastic_patternfly4 import Select


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
        ".//button[contains(@class, 'pf-c-context-selector__toggle')]"
    )
    ITEMS_LOCATOR = ".//ul/li/button | .//ul/li/a"
    ITEM_LOCATOR = ".//ul/li/button | .//ul/li/a[normalize-space(.)={}]"

    def __init__(self, parent, locator, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.locator = locator

    @property
    def is_open(self):
        """Returns True if the Dropdown is open"""
        return "open" or "pf-m-expanded" in self.browser.classes(self)


class SortSelector(SelectorDropdown):
    def item_select(self, item, *args, **kwargs):
        super(SelectorDropdown, self).item_select(item, *args, **kwargs)
        wait_for(lambda: self.currently_selected.lower() == item.lower(), num_sec=3, delay=0.2)


class TransformationPath(Widget):
    ROOT = './/div[contains(@class,"pf-c-empty-state__content")]'

    @ParametrizedView.nested
    class _card(ParametrizedView):
        PARAMETERS = ("card_name",)
        card = Text(ParametrizedLocator("//h4[contains(normalize-space(.), {card_name|quote})]"))

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

    def show_report(self):
        self.browser.click(self.SHOW_REPORT)
        self.switch_to_report()

    def switch_to_report(self):
        """Switch focus to report window."""
        main_window = self.browser.current_window_handle
        open_url_window = (set(self.browser.window_handles) - {main_window}).pop()
        self.browser.switch_to_window(open_url_window)


class HiddenFileInput(FileInput):
    """Uploads file via hidden input form field

    Prerequisite:
        Type of input field should be file (type='file')
    """

    def fill(self, filepath):
        self.browser.set_attribute("style", "display: none;", self)
        self.browser.send_keys(filepath, self)

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


class MTASelect(Select):
    """Select for MTA"""

    BUTTON_LOCATOR = ".//button[contains(@class, 'pf-c-select__toggle-button')]"


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
