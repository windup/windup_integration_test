from taretto.navigate import NavigateToAttribute
from taretto.navigate import NavigateToSibling
from wait_for import wait_for
from widgetastic.utils import WaitFillViewStrategy
from widgetastic.widget import Checkbox
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
from selenium.common.exceptions import NoSuchElementException


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
    table_loading = './/div[contains(@class, "pf-c-skeleton")]'
    ACTIONS_INDEX = 4
    title = Text(locator=".//div[contains(@class, 'pf-c-empty-state__content')]/h4")
    table = Table(
        locator='.//table[contains(@aria-label, "Table")]',
        column_widgets={
            "Short path": Button(locator='.//th[@data-label="Short path"]/button'),
            ACTIONS_INDEX: Dropdown(),
        },
    )

    def is_table_loaded(self):
        return wait_for(
            lambda: not self.browser.is_displayed(self.table_loading), delay=10, timeout=240
        )

    @property
    def is_displayed(self):
        if self.is_table_loaded():
            return self.add_rule_button.is_displayed and (
                self.table.is_displayed or self.title.is_displayed
            )
        else:
            return False


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


class AddCustomRuleServerPathView(CustomRulesView):
    rules_path = Input(id="serverPath")
    scan_recursive = Checkbox("isChecked")
    save_button = Button("Save")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.rules_path.is_displayed and self.cancel_button.is_displayed


class AddCustomRuleView(CustomRulesView):
    title = Text(locator=".//h1[contains(normalize-space(.), 'Add rules')]")
    upload_rule = HiddenFileInput(locator='.//input[contains(@accept,".xml")]')
    file_uploaded = './/div[contains(@class, "pf-m-success")]'
    browse_button = Button("Browse")
    close_button = Button("Close")

    @View.nested
    class server_path(MTATab):  # noqa
        TAB_NAME = "Server path"
        including_view = View.include(AddCustomRuleServerPathView, use_parent=True)

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

    def upload_custom_rule_file(self, server_path=False, scan_recursive=False):
        """Method for uploading custom rule file

        server_path: if True then upload rule file by server path
        scan_recursive: If True and the given path is a directory, the subdirectories will also be
        scanned for rule sets
        """
        view = navigate_to(self, "Add")
        if server_path:
            # upload custom rules by providing server path to folder of rule files
            env = conf.get_config("env")
            fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
            file_path = fs1.download(self.file_name)
            rules_path = file_path.split(self.file_name)[0]
            view.server_path.click()
            view.server_path.rules_path.fill(rules_path)
            if scan_recursive:
                view.server_path.scan_recursive.click()
            view.server_path.save_button.click()
        else:
            # upload custom rules by browsing rule files
            env = conf.get_config("env")
            fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
            file_path = fs1.download(self.file_name)
            view.upload_rule.fill(file_path)
            wait_for(lambda: view.browser.is_displayed(view.file_uploaded), delay=10, timeout=60)
            view.close_button.click()

    def delete_custom_rule(self, cancel=False):
        """Method to delete custom rule file
        Args:
             cancel
        """
        view = navigate_to(self, "Delete")
        view.wait_displayed("30s")
        if cancel:
            view.cancel_button.click()
        else:
            view.delete_button.click()
        view = self.create_view(CustomRulesView)
        wait_for(lambda: view.is_displayed, delay=10, timeout=240)
        try:
            return self.file_name not in [row.read()["Short path"] for row in view.table]
        except NoSuchElementException:
            view.browser.refresh()
            view.delete_button.click()
            view = self.create_view(CustomRulesView)
            wait_for(lambda: view.is_displayed, delay=10, timeout=240)


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
        self.view.wait_displayed("20s")


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
        self.prerequisite_view.wait_displayed("30s")
        for row in self.prerequisite_view.table:
            if row.read()["Short path"] == self.obj.file_name:
                row[self.prerequisite_view.ACTIONS_INDEX].widget.item_select("Delete")
