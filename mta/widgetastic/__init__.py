from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import FileInput
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic.widget import Widget
from widgetastic_patternfly import AggregateStatusCard
from widgetastic_patternfly import Button
from widgetastic_patternfly import Dropdown
from widgetastic_patternfly import SelectorDropdown
from widgetastic_patternfly import VerticalNavigation

from mta.exceptions import ProjectNotFound


class HOMENavigation(VerticalNavigation):
    """The Patternfly Vertical navigation for Home Icon (Projects)"""

    CURRENTLY_SELECTED = './/li[contains(@class, "home")]/a/span'


class MTANavigation(VerticalNavigation):
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


class SortSelector(SelectorDropdown):
    def item_select(self, item, *args, **kwargs):
        super(SelectorDropdown, self).item_select(item, *args, **kwargs)
        wait_for(lambda: self.currently_selected.lower() == item.lower(), num_sec=3, delay=0.2)


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


class ProjectList(View):
    """This is custom widget represent project list and provide actions to project

    .. code-block:: python

        from mta.widgetastic import ProjectList
        projects = ProjectList(view, locator=".//div[contains(@class, 'projects-list')]")

        projects.items          # >> ['test', 'test_2', 'test_project_2']
        projects.projects       # >> [Project(test), Project(test_2), Project(test_project_2)]
        proj = projects.get_project("test_2")
        proj                    # >> Project(test_2)
        proj.name               # >> 'test_2'
        proj.description        # >> 'adsfsaf'
        proj.application_count  # >> '1 application'
        proj.last_updated       # >> 'Last updated 4 hours ago'
        proj.edit()             # open edit dialog
        proj.delete()           # open delete dialog
    """

    ROOT = ParametrizedLocator("{@locator}")
    LIST_ITEM_LOCATOR = ".//div[contains(@class, 'list-group-item  project-info')]"
    TITLE_LOCATOR = ".//h2[contains(@class, 'project-title')]"

    def __init__(self, parent, locator=None, logger=None):
        View.__init__(self, parent, logger=logger)
        self.locator = locator

    @ParametrizedView.nested
    class project(ParametrizedView):  # noqa
        """Parametrized project selection"""

        PARAMETERS = ("name",)

        ROOT = ParametrizedLocator(
            ".//div[contains(@class, 'list-group-item  project-info') "
            "and .//h2[text()={name|quote}]]"
        )

        TITLE_LOCATOR = ".//h2[contains(@class, 'project-title')]"
        DESCRIPTION_LOCATOR = ".//div[contains(@class, 'list-group-item-text description')]"
        APPLICATION_COUNT = ".//small[contains(@class, 'count-applications')]"
        LAST_UPDATED = ".//small[contains(@class, 'last-updated')]"
        DELETE_PROJECT = ".//a[contains(@class,'action-button action-delete-project')]"
        EDIT_PROJECT = ".//a[contains(@class,'action-button action-edit-project')]"

        @property
        def name(self):
            """return name of project"""
            return self.browser.text(self.TITLE_LOCATOR)

        @property
        def description(self):
            """return description of project"""
            return self.browser.text(self.DESCRIPTION_LOCATOR)

        @property
        def application_count(self):
            """return application count text"""
            return self.browser.text(self.APPLICATION_COUNT)

        @property
        def last_updated(self):
            """return last project updated info"""
            return self.browser.text(self.LAST_UPDATED)

        def delete(self):
            """click on delete project"""
            self.browser.click(self.DELETE_PROJECT)

        def edit(self):
            """click on edit project"""
            self.browser.click(self.EDIT_PROJECT)

        def select(self):
            """click on specific project"""
            self.browser.click(self.TITLE_LOCATOR)

        def __repr__(self):
            return f"Project({self.name})"

    @property
    def items(self):
        """return all project names"""
        return [
            self.browser.text(self.TITLE_LOCATOR, parent=item)
            for item in self.browser.elements(self.LIST_ITEM_LOCATOR)
        ]

    def read(self):
        return self.items

    @property
    def projects(self):
        """return all available project objects"""
        return [self.project(item) for item in self.items]

    def get_project(self, name):
        """ Get specific project
        Args:
            name: name of project
        Returns:
            list of project objects
        """
        if name in self.items:
            return self.project(name)
        else:
            raise ProjectNotFound(f"Project {name} not found.")

    def select_project(self, name):
        """ Select specific project
            Args:
                name: name of project
        """
        project = self.get_project(name)
        project.select()


class AnalysisResults(Widget):
    # When there are multiple analysis the first row is latest one
    # so we need to check spinner and success in 1st row
    SPINNER_LOCATOR = (
        './/tr[contains(@class, "info")]/td[2]/wu-status-icon'
        '/span[contains(@class, "status-icon")]/span[contains(@class,"spinner")]'
    )
    COMPLETE_STATUS_LOCATOR = (
        './/tr[1]/td[2]//wu-status-icon/span/span[contains(@class, "fa fa-check")]'
    )
    SHOW_REPORT = './/i[contains(@class,"fa fa-bar-chart")]'

    def in_progress(self):
        return self.browser.is_displayed(self.SPINNER_LOCATOR)

    def is_analysis_complete(self):
        """Returns True if analysis complete and spinner not present"""
        return self.browser.is_displayed(self.COMPLETE_STATUS_LOCATOR)

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
        self.browser.set_attribute("style", "position", self)
        self.browser.send_keys(filepath, self)

    @property
    def is_displayed(self):
        self.browser.set_attribute("style", "position", self)
        return self.browser.is_displayed(self)


class AddButton(Button):
    """Multiple buttons with same name are present in UI.
       So need to specify the locator.
    """

    def __locator__(self):
        return ".//button[text()='Cancel']/following-sibling::button"
