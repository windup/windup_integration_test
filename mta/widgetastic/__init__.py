from selenium.webdriver.common.keys import Keys
from wait_for import wait_for
from widgetastic.utils import Parameter
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import FileInput
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Select
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic.widget import Widget
from widgetastic_patternfly import AggregateStatusCard
from widgetastic_patternfly import Button
from widgetastic_patternfly import Input
from widgetastic_patternfly import SelectorDropdown
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import Navigation


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
    BUTTON_LOCATOR = ".//button[contains(@class, 'pf-c-context-selector__toggle')]"
    ITEMS_LOCATOR = ".//ul/li/button"
    ITEM_LOCATOR = ".//ul/li/button"

    def __init__(self, parent, locator, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.locator = locator


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
        self.browser.send_keys(f"{Keys.CONTROL}+a", self)
        self.browser.send_keys(value, self)
        return True


class MultiBoxSelect(View):

    """This view combines two `<select>` elements and buttons for moving items between them.
    This view can be found in policy profile, alert profiles adding screens; assigning actions to an
    event, assigning conditions to a policy screens and so on.
    Args:
        available_items (str): provided value of `<select>` id for available items
        chosen_items (str): provided value of `<select>` id for available items
        move_into (str): provided value of `data-submit` attribute for 'move_into' button
        move_from (str): provided value of `data-submit` attribute for 'move_from' button
    """

    available_options = Select(id=Parameter("@available_items"))
    chosen_options = Select(id=Parameter("@chosen_items"))
    move_into_button = Button(**{"data-submit": Parameter("@move_into")})
    move_from_button = Button(**{"data-submit": Parameter("@move_from")})

    def __init__(
        self,
        parent,
        move_into="choices_chosen_div",
        move_from="members_chosen_div",
        available_items="choices_chosen",
        chosen_items="members_chosen",
        logger=None,
    ):
        View.__init__(self, parent, logger=logger)
        self.available_items = available_items
        self.chosen_items = chosen_items
        self.move_into = move_into
        self.move_from = move_from

    def _values_to_remove(self, values):
        return list(set(self.all_options) - set(values))

    def _values_to_add(self, values):
        return list(set(values) - set(self.all_options))

    def fill(self, values):
        if set(values) == self.all_options:
            return False
        else:
            values_to_remove = self._values_to_remove(values)
            values_to_add = self._values_to_add(values)
            if values_to_remove:
                self.chosen_options.fill(values_to_remove)
                self.move_from_button.click()
                self.browser.plugin.ensure_page_safe()
            if values_to_add:
                self.available_options.fill(values_to_add)
                self.move_into_button.click()
                self.browser.plugin.ensure_page_safe()
            return True

    @property
    def all_options(self):
        return [option.text for option in self.chosen_options.all_options]

    def read(self):
        return self.all_options
