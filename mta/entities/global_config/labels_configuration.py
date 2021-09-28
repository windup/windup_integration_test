from taretto.navigate import NavigateToAttribute
from taretto.navigate import NavigateToSibling
from wait_for import wait_for
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
from mta.widgetastic import HiddenFileInput
from mta.widgetastic import Input
from mta.widgetastic import MTATab


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


class CustomLabelsView(BaseLoggedInPage):
    """This view represents Custom labels tab page"""

    paginator = Pagination(locator='.//div[contains(@class, "pf-c-pagination")]')
    add_label_button = Button("Add label")
    search = Input(locator=".//input[@aria-label='Filter by short path']")
    table_loading = './/div[contains(@class, "pf-c-skeleton")]'
    ACTIONS_INDEX = 2
    table = Table(
        locator='.//table[contains(@aria-label, "Table")]',
        column_widgets={
            "Short path": Button(locator='.//th[@data-label="Short path"]/button'),
            ACTIONS_INDEX: Dropdown(),
        },
    )

    def is_table_loaded(self):
        return wait_for(
            lambda: not self.browser.is_displayed(self.table_loading), delay=10, timeout=120
        )

    @property
    def is_displayed(self):
        if self.is_table_loaded():
            return self.add_label_button.is_displayed and self.table.is_displayed
        else:
            return False


class AddCustomLabelView(View):
    title = Text(locator=".//h1[contains(normalize-space(.), 'Add labels')]")
    upload_label = HiddenFileInput(locator='.//input[contains(@accept,".xml")]')
    file_uploaded = './/div[contains(@class, "pf-m-success")]'
    browse_button = Button("Browse")
    close_button = Button("Close")
    fill_strategy = WaitFillViewStrategy("15s")

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.browse_button.is_displayed


class DeleteCustomLabelView(View):
    title = Text(locator=".//h1[contains(normalize-space(.), 'Delete')]")
    fill_strategy = WaitFillViewStrategy("35s")

    delete_button = Button("Delete")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.delete_button.is_displayed


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


class SystemLabelsConfigurations(Updateable, NavigatableMixin):
    """Class for representing all the global_1 custom/system labels methods/operations"""

    def __init__(self, application):
        self.application = application

    def search_system_labels(self, provider_id):
        """Method for searching system labels"""
        view = navigate_to(self, "SystemLabel")
        view.search.fill(provider_id)


class CustomLabelsConfigurations(Updateable, NavigatableMixin):
    """Class for representing all the global_1 custom/system labels methods/operations"""

    def __init__(self, application, file_name):
        self.application = application
        self.file_name = file_name

    def upload_custom_label_file(self):
        """Method for uploading custom label file
        """
        view = navigate_to(self, "Add")
        view.wait_displayed("20s")
        # upload custom labels
        env = conf.get_config("env")
        fs1 = FTPClientWrapper(env.ftpserver.entities.mta)
        file_path = fs1.download(self.file_name)
        view.upload_label.fill(file_path)
        wait_for(lambda: view.browser.is_displayed(view.file_uploaded), delay=10, timeout=30)
        view.close_button.click()

    def delete_custom_label_file(self, cancel=False):
        """Method for deleting custom label file
        Args:
            cancel
        """
        view = navigate_to(self, "Delete")
        view.wait_displayed("30s")

        if cancel:
            view.cancel_button.click()
        else:
            view.delete_button.click()
        view = self.create_view(CustomLabelsView)
        view.wait_displayed("20s")
        return self.file_name not in [row.read()["Short path"] for row in view.table]

    def search_system_labels(self, provider_id):
        """Method for searching system labels"""
        view = navigate_to(self, "SystemLabel")
        view.search.fill(provider_id)


@ViaWebUI.register_destination_for(SystemLabelsConfigurations, "AllLabels")
@ViaWebUI.register_destination_for(CustomLabelsConfigurations, "AllLabels")
class AllLabels(MTANavigateStep):
    VIEW = LabelsConfigurationView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self):
        self.prerequisite_view.navigation.select("Labels configuration")


@ViaWebUI.register_destination_for(SystemLabelsConfigurations, "SystemLabel")
class SystemLabel(MTANavigateStep):
    VIEW = SystemLabelsView
    prerequisite = NavigateToSibling("AllLabels")

    def step(self):
        self.prerequisite_view.system_labels.click()


@ViaWebUI.register_destination_for(CustomLabelsConfigurations, "CustomLabel")
class CustomLabel(MTANavigateStep):
    VIEW = CustomLabelsView
    prerequisite = NavigateToSibling("AllLabels")

    def step(self):
        self.prerequisite_view.custom_labels.click()


@ViaWebUI.register_destination_for(CustomLabelsConfigurations, "Add")
class CustomLabelAdd(MTANavigateStep):
    VIEW = AddCustomLabelView
    prerequisite = NavigateToSibling("CustomLabel")

    def step(self):
        self.prerequisite_view.add_label_button.click()


@ViaWebUI.register_destination_for(CustomLabelsConfigurations, "Delete")
class CustomLabelDelete(MTANavigateStep):
    VIEW = DeleteCustomLabelView
    prerequisite = NavigateToSibling("CustomLabel")

    def step(self):
        for row in self.prerequisite_view.table:
            if row.read()["Short path"] == self.obj.file_name:
                row[self.prerequisite_view.ACTIONS_INDEX].widget.item_select("Delete")
