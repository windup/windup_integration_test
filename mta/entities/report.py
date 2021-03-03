from widgetastic.utils import WaitFillViewStrategy
from widgetastic.widget import View
from widgetastic_patternfly import Tab
from widgetastic_patternfly import Text

from mta.entities import BaseLoggedInPage
from mta.widgetastic import FilterInput
from mta.widgetastic import MTADropdownMenu


class AllApplicationsView(BaseLoggedInPage):

    APP_ITEMS_LOCATOR = './/div[contains(@class, "fileName")]/a'

    filter_application = FilterInput(id="filter")
    title = Text(locator=".//div[text()[normalize-space(.)='Application List']]")
    send_feedback = Text(locator=".//a[contains(text(), 'Send Feedback')]")

    clear = Text('.//a[@id="clear-filters"]')

    filter_selector = MTADropdownMenu(
        locator='.//span[@class="filter-by"]/parent::button/parent::div'
    )

    @property
    def clear_filters(self):
        if self.clear.is_displayed:
            self.clear.click()

    def search(self, search_value, filter_type="Name", clear_filters=False):
        """Fill input box with 'search_value', use 'filter_type' to choose filter selector.
        If no filter_type is entered then the default for page is used.
        """
        if clear_filters:
            self.clear_filters()
        if filter_type:
            self.filter_selector.item_select(filter_type)
        self.filter_application.fill(search_value)

    @property
    def get_applications_list(self):
        """Returns list of applications by name"""
        result = [self.browser.text(el) for el in self.browser.elements(self.APP_ITEMS_LOCATOR)]
        return result

    @property
    def is_displayed(self):
        return self.filter_application.is_displayed and self.title.is_displayed

    @View.nested
    class tabs(View):  # noqa
        """The tabs on the page"""

        @View.nested
        class all_issues(Tab):  # noqa
            fill_strategy = WaitFillViewStrategy("15s")
            TAB_NAME = "All Issues"
            title = Text('.//div[contains(@class, "page-header")]/h1/div')

            @property
            def is_displayed(self):
                return self.title.text == "All Issues"

        @View.nested
        class technologies(Tab):  # noqa
            fill_strategy = WaitFillViewStrategy("20s")
            TAB_NAME = "Technologies"
            title = Text('.//div[contains(@class, "page-header")]/h1/div')

            @property
            def is_displayed(self):
                return self.title.text == "Technologies"
