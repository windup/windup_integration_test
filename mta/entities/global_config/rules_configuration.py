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
from mta.base.application.implementations.web_ui import NavigatableMixin
from mta.base.application.implementations.web_ui import navigate_to
from mta.base.application.implementations.web_ui import ViaWebUI
from mta.entities import BaseLoggedInPage
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper
from mta.utils.update import Updateable
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

    @property
    def is_displayed(self):
        return self.table.is_displayed and self.show_all_rules.is_displayed


class CustomRulesView(BaseLoggedInPage):
    """This view represents Custom rules tab page"""

    paginator = Pagination(locator='.//div[contains(@class, "pf-c-pagination")]')
    add_rule_button = Button("Add rule")
    search = Input(locator=".//input[@aria-label='Filter by short path']")
    ACTIONS_INDEX = 4
    table = Table(
        locator='.//table[contains(@aria-label, "Table")]',
        column_widgets={
            "Short path": Button(locator='.//th[@data-label="Short path"]/button'),
            ACTIONS_INDEX: Dropdown(),
        },
    )

    @property
    def is_displayed(self):
        return self.add_rule_button.is_displayed and self.table.is_displayed


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


class AddCustomRuleView(CustomRulesView):
    title = Text(locator=".//h1[contains(normalize-space(.), 'Add rules')]")
    upload_rule = HiddenFileInput(locator='.//input[contains(@accept,".xml")]')
    browse_button = Button("Browse")
    close_button = Button("Close")
    fill_strategy = WaitFillViewStrategy("15s")

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.browse_button.is_displayed


class DeleteCustomRuleView(CustomRulesView):
    title = Text(locator=".//h1[contains(normalize-space(.), 'Delete')]")
    fill_strategy = WaitFillViewStrategy("35s")

    delete_button = Button("Delete")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.delete_button.is_displayed


class SystemRulesConfiguration(Updateable, NavigatableMixin):
    """Class for representing all the global_1 custom/system rules methods/operations"""

    def __init__(self, application):
        self.application = application

    def clear_filters(self):
        """Method to clear all the system filters"""
        view = navigate_to(self, "SystemRule")
        view.wait_displayed()

        if view.clear.is_displayed:
            view.clear.click()

    def search_system_rules(self, search_value, filter_type="Source", clear_filters=False):
        """Fill input box with 'search_value', use 'filter_type' to choose filter selector.
        If no filter_type is entered then the default for page is used.
        """
        view = navigate_to(self, "SystemRule")
        view.wait_displayed()

        if clear_filters:
            self.clear_filters()
        if filter_type:
            view.filter_type_selector.item_select(filter_type)
        view.filter_by.item_select(search_value)


class CustomRulesConfiguration(Updateable, NavigatableMixin):
    """Class for representing all the global_1 custom/system rules methods/operations"""

    def __init__(self, application, file_name):
        self.application = application
        self.file_name = file_name

    def upload_custom_rule_file(self):
        """Method for uploading custom rule file
        """
        view = navigate_to(self, "Add")
        view.wait_displayed("20s")
        # upload custom rules
        env = conf.get_config("env")
        fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
        file_path = fs1.download(self.file_name)
        view.upload_rule.fill(file_path)
        view.close_button.click()

    def delete_custom_rule(self, cancel=False):
        """Method to delete custom rule file
        Args:
             cancel
        """
        view = navigate_to(self, "Delete")
        view.wait_displayed()

        if cancel:
            view.cancel_button.click()
        else:
            view.delete_button.click()
        view = self.create_view(CustomRulesView)
        view.wait_displayed("30s")
        return self.file_name not in [row.read()["Short path"] for row in view.table]


@ViaWebUI.register_destination_for(SystemRulesConfiguration, "AllRules")
@ViaWebUI.register_destination_for(CustomRulesConfiguration, "AllRules")
class AllRules(MTANavigateStep):
    VIEW = RulesConfigurationView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self):
        self.prerequisite_view.navigation.select("Rules configuration")


@ViaWebUI.register_destination_for(SystemRulesConfiguration, "SystemRule")
class SystemRule(MTANavigateStep):
    VIEW = SystemRulesView
    prerequisite = NavigateToSibling("AllRules")

    def step(self):
        self.prerequisite_view.system_rules.click()


@ViaWebUI.register_destination_for(CustomRulesConfiguration, "CustomRule")
class CustomRule(MTANavigateStep):
    VIEW = CustomRulesView
    prerequisite = NavigateToSibling("AllRules")

    def step(self):
        self.prerequisite_view.custom_rules.click()


@ViaWebUI.register_destination_for(CustomRulesConfiguration, "Add")
class CustomRuleAdd(MTANavigateStep):
    VIEW = AddCustomRuleView
    prerequisite = NavigateToSibling("CustomRule")

    def step(self):
        self.prerequisite_view.add_rule_button.click()


@ViaWebUI.register_destination_for(CustomRulesConfiguration, "Delete")
class CustomRuleDelete(MTANavigateStep):
    VIEW = DeleteCustomRuleView
    prerequisite = NavigateToSibling("CustomRule")

    def step(self):
        for row in self.prerequisite_view.table:
            if row.read()["Short path"] == self.obj.file_name:
                row[self.prerequisite_view.ACTIONS_INDEX].widget.item_select("Delete")
