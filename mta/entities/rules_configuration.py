import attr
from taretto.navigate import NavigateToAttribute
from taretto.navigate import NavigateToSibling
from widgetastic.utils import WaitFillViewStrategy
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly4 import Button
from widgetastic_patternfly4 import Dropdown
from widgetastic_patternfly4 import Pagination
from widgetastic_patternfly4.table import Table

from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.web_ui import ViaWebUI
from mta.base.modeling import BaseCollection
from mta.entities import BaseLoggedInPage
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper
from mta.widgetastic import DropdownMenu
from mta.widgetastic import HiddenFileInput
from mta.widgetastic import Input
from mta.widgetastic import MTACheckboxSelect
from mta.widgetastic import MTATab


class SystemRulesView(BaseLoggedInPage):
    """This view represents System rules tab page"""

    paginator = Pagination(locator='.//div[contains(@class, "pf-c-pagination")]')

    show_all_rules = Text(".//input[@id='showAllRules']")
    table = Table(
        locator='.//table[contains(@aria-label, "Table")]',
        column_widgets={
            "Provider ID": Button(locator='.//th[@data-label="Provider ID"]/button'),
            "Number of rules": Button(locator=".//th[@data-label='Number of rules']/button"),
            4: Dropdown(),
        },
    )
    filter_type_selector = DropdownMenu(locator='.//div[contains(@class, "pf-c-select")]')
    filter_by = MTACheckboxSelect(
        locator='.//span[@class="pf-c-select__toggle-arrow"]//parent::button['
        'contains(@aria-labelledby, "Filter by Source")]/parent::div |'
        ' .//span[@class="pf-c-select__toggle-arrow"]//parent::button['
        'contains(@aria-labelledby, "Filter by Target")]/parent::div'
    )

    clear = Text('.//button[contains(text(), "Clear all filters")]')

    def clear_filters(self):
        if self.clear.is_displayed:
            self.clear.click()

    def search(self, search_value, filter_type="Source", clear_filters=False):
        """Fill input box with 'search_value', use 'filter_type' to choose filter selector.
        If no filter_type is entered then the default for page is used.
        """
        if clear_filters:
            self.clear_filters()
        if filter_type:
            self.filter_type_selector.item_select(filter_type)
        self.filter_by.item_select(search_value)


class DeleteCustomRuleView(View):
    title = Text(locator=".//h1[contains(normalize-space(.), 'Delete')]")
    fill_strategy = WaitFillViewStrategy("35s")

    delete_button = Button("Delete")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.delete_button.is_displayed


class CustomRulesView(BaseLoggedInPage):
    """This view represents Custom rules tab page"""

    paginator = Pagination(locator='.//div[contains(@class, "pf-c-pagination")]')
    add_rule_button = Button("Add rule")
    search = Input(locator=".//input[@aria-label='Filter by short path']")
    table = Table(
        locator='.//table[contains(@aria-label, "Table")]',
        column_widgets={
            "Short path": Button(locator='.//th[@data-label="Short path"]/button'),
            4: Dropdown(),
        },
    )
    delete_rules = View.nested(DeleteCustomRuleView)

    @property
    def is_displayed(self):
        return self.add_rule_button.is_displayed and self.table.is_displayed

    @View.nested
    class custom_rules(View):  # noqa
        upload_rule = HiddenFileInput(locator='.//input[contains(@accept,".xml")]')
        close_button = Button("Close")
        fill_strategy = WaitFillViewStrategy("15s")

        def upload_rule_file(self, value):
            """
            Args:
                values: custom rule file to be uploaded
            """
            self.wait_displayed()
            self.parent.add_rule_button.click()
            # upload custom rules
            env = conf.get_config("env")
            fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
            file_path = fs1.download(value)
            self.upload_rule.fill(file_path)
            self.close_button.click()

        def delete(self, file_name, cancel=False):
            """
            Method to delete custom rule file
            :param file_name: file name to delete
            """
            for row in self.parent.table:
                if row.read()["Short path"] == file_name:
                    row[4].widget.item_select("Delete")
            if cancel:
                self.parent.delete_rules.cancel_button.click()
            else:
                self.parent.delete_rules.delete_button.click()
            self.parent.wait_displayed()
            return file_name not in [row.read()["Short path"] for row in self.parent.table]


class RulesConfigurationView(BaseLoggedInPage):
    """This view is for presenting rules configuration page"""

    title = Text(locator=".//h1")

    @View.nested
    class system_rules(MTATab):  # noqa
        TAB_NAME = "System rules"
        including_view = View.include(SystemRulesView, use_parent=True)

    @View.nested
    class custom_rules(MTATab):  # noqa
        TAB_NAME = "Custom rules"
        including_view = View.include(CustomRulesView, use_parent=True)

    @property
    def is_displayed(self):
        return (
            self.title.text == "Rules configuration"
            and self.system_rules.is_displayed
            and self.custom_rules.is_displayed
        )


@attr.s
class GlobalRulesCollection(BaseCollection):
    pass


@ViaWebUI.register_destination_for(GlobalRulesCollection, "All")
class All(MTANavigateStep):
    VIEW = RulesConfigurationView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self):
        self.prerequisite_view.navigation.select("Rules configuration")


@ViaWebUI.register_destination_for(GlobalRulesCollection, "System")
class System(MTANavigateStep):
    VIEW = SystemRulesView
    prerequisite = NavigateToSibling("All")

    def step(self):
        self.prerequisite_view.system_rules.click()


@ViaWebUI.register_destination_for(GlobalRulesCollection, "Custom")
class Custom(MTANavigateStep):
    VIEW = CustomRulesView
    prerequisite = NavigateToSibling("All")

    def step(self):
        self.prerequisite_view.custom_rules.click()
