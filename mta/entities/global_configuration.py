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

# All Global Rule's views


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
    upload_rule = HiddenFileInput(locator='.//input[contains(@accept,".xml")]')
    close_button = Button("Close")
    fill_strategy = WaitFillViewStrategy("15s")

    delete_rules = View.nested(DeleteCustomRuleView)

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


# All Global Label's views


class SystemLabelsView(BaseLoggedInPage):
    """This view represents System labels tab page"""

    paginator = Pagination(locator='.//div[contains(@class, "pf-c-pagination")]')

    table = Table(
        locator='.//table[contains(@aria-label, "Table")]',
        column_widgets={
            "Provider ID": Button(locator='.//th[@data-label="Provider ID"]/button'),
            2: Dropdown(),
        },
    )
    search = Input(locator='.//input[@aria-label="Filter by provider ID"]')

    @property
    def is_displayed(self):
        return self.table.is_displayed and self.search.is_displayed


class DeleteCustomLabelView(View):
    title = Text(locator=".//h1[contains(normalize-space(.), 'Delete')]")
    fill_strategy = WaitFillViewStrategy("35s")

    delete_button = Button("Delete")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.delete_button.is_displayed


class CustomLabelsView(BaseLoggedInPage):
    """This view represents Custom labels tab page"""

    paginator = Pagination(locator='.//div[contains(@class, "pf-c-pagination")]')
    add_label_button = Button("Add label")
    search = Input(locator=".//input[@aria-label='Filter by short path']")
    table = Table(
        locator='.//table[contains(@aria-label, "Table")]',
        column_widgets={
            "Short path": Button(locator='.//th[@data-label="Short path"]/button'),
            2: Dropdown(),
        },
    )
    upload_label = HiddenFileInput(locator='.//input[contains(@accept,".xml")]')
    close_button = Button("Close")
    fill_strategy = WaitFillViewStrategy("15s")

    delete_labels = View.nested(DeleteCustomLabelView)

    @property
    def is_displayed(self):
        return self.add_label_button.is_displayed and self.table.is_displayed


class LabelsConfigurationView(BaseLoggedInPage):
    """This view is for presenting Labels configuration page"""

    title = Text(locator=".//h1")

    @View.nested
    class system_labels(MTATab):  # noqa
        TAB_NAME = "System labels"
        including_view = View.include(SystemLabelsView, use_parent=True)

    @View.nested
    class custom_labels(MTATab):  # noqa
        TAB_NAME = "Custom labels"
        including_view = View.include(CustomLabelsView, use_parent=True)

    @property
    def is_displayed(self):
        return (
            self.title.text == "Labels configuration"
            and self.system_labels.is_displayed
            and self.custom_labels.is_displayed
        )


class GlobalConfigurations(Updateable, NavigatableMixin):
    """Class for representing all the global custom/system rules/labels methods/operations"""

    def __init__(self, application):
        self.application = application

    def upload_custom_label_file(self, value):
        """Method for uploading custom label file
        Args:
            value: custom label file to be uploaded
        """
        view = navigate_to(self, "CustomLabel")
        view.wait_displayed()
        view.add_label_button.click()
        # upload custom labels
        env = conf.get_config("env")
        fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
        file_path = fs1.download(value)
        view.upload_label.fill(file_path)
        view.close_button.click()

    def delete_custom_label_file(self, file_name, cancel=False):
        """Method for deleting custom label file
        :param file_name: file name to delete
        """
        view = navigate_to(self, "CustomLabel")
        view.wait_displayed()
        for row in view.table:
            if row.read()["Short path"] == file_name:
                row[2].widget.item_select("Delete")
        if cancel:
            view.delete_labels.cancel_button.click()
        else:
            view.delete_labels.delete_button.click()
        view.wait_displayed()
        return file_name not in [row.read()["Short path"] for row in view.table]

    def search_system_labels(self, provider_id):
        """Method for searching system labels"""
        view = navigate_to(self, "SystemLabel")
        view.search.fill(provider_id)

    def upload_custom_rule_file(self, value):
        """Method for uploading custom rule file
        Args:
            value: custom rule file to be uploaded
        """
        view = navigate_to(self, "CustomRule")
        view.wait_displayed()
        view.add_rule_button.click()
        # upload custom rules
        env = conf.get_config("env")
        fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
        file_path = fs1.download(value)
        view.upload_rule.fill(file_path)
        view.close_button.click()

    def delete_custom_rule(self, file_name, cancel=False):
        """Method to delete custom rule file
        :param file_name: file name to delete
        """
        view = navigate_to(self, "CustomRule")
        view.wait_displayed()

        for row in view.table:
            if row.read()["Short path"] == file_name:
                row[4].widget.item_select("Delete")
        if cancel:
            view.delete_rules.cancel_button.click()
        else:
            view.delete_rules.delete_button.click()
        view.wait_displayed()
        return file_name not in [row.read()["Short path"] for row in view.table]

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


@ViaWebUI.register_destination_for(GlobalConfigurations, "AllRules")
class AllRules(MTANavigateStep):
    VIEW = RulesConfigurationView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self):
        self.prerequisite_view.navigation.select("Rules configuration")


@ViaWebUI.register_destination_for(GlobalConfigurations, "AllLabels")
class AllLabels(MTANavigateStep):
    VIEW = LabelsConfigurationView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self):
        self.prerequisite_view.navigation.select("Labels configuration")


@ViaWebUI.register_destination_for(GlobalConfigurations, "SystemRule")
class SystemRule(MTANavigateStep):
    VIEW = SystemRulesView
    prerequisite = NavigateToSibling("AllRules")

    def step(self):
        self.prerequisite_view.system_rules.click()


@ViaWebUI.register_destination_for(GlobalConfigurations, "CustomRule")
class CustomRule(MTANavigateStep):
    VIEW = CustomRulesView
    prerequisite = NavigateToSibling("AllRules")

    def step(self):
        self.prerequisite_view.custom_rules.click()


@ViaWebUI.register_destination_for(GlobalConfigurations, "SystemLabel")
class SystemLabel(MTANavigateStep):
    VIEW = SystemLabelsView
    prerequisite = NavigateToSibling("AllLabels")

    def step(self):
        self.prerequisite_view.system_labels.click()


@ViaWebUI.register_destination_for(GlobalConfigurations, "CustomLabel")
class CustomLabel(MTANavigateStep):
    VIEW = CustomLabelsView
    prerequisite = NavigateToSibling("AllLabels")

    def step(self):
        self.prerequisite_view.custom_labels.click()
