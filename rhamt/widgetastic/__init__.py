from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic.widget import Widget
from widgetastic_patternfly import AggregateStatusCard
from widgetastic_patternfly import Dropdown
from widgetastic_patternfly import VerticalNavigation


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


class ProjectList(Widget):
    ROOT = ParametrizedLocator(".//div[contains(@class,{@locator|quote})]")
    LIST_ITEM_LOCATOR = './div[contains(@class,"list-group-item")]'
    PROJECT_LOCATOR = './/div[contains(@class,"list-group-item-heading")]' "/a/h2"
    # TO DO implement delete and edit methods
    DELETE_PROJECT = './/span/a[contains(@title, "Delete project")]'
    EDIT_PROJECT = './/span/a[contains(@class,"Edit Project")]'

    def __init__(self, parent, locator, logger=None):
        Widget.__init__(self, parent, logger=logger)
        self.locator = locator

    @property
    def items(self):
        return [self.browser.text(item) for item in self.browser.elements(self.PROJECT_LOCATOR)]

    def read(self):
        return self.items
