from widgetastic.utils import WaitFillViewStrategy
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly import Tab

from mta.entities import BaseLoggedInPage
from mta.widgetastic import Input


class AllApplicationsView(BaseLoggedInPage):

    filter_by_name = Input(id="filter")
    title = Text(locator=".//div[text()[normalize-space(.)='Application List']]")
    send_feedback = Text(locator=".//a[contains(text(), 'Send Feedback')]")

    @property
    def is_displayed(self):
        return self.filter_by_name.is_displayed and self.title.is_displayed

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
