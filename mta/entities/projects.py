from sys import platform

import attr
from taretto.navigate import NavigateToAttribute
from taretto.navigate import NavigateToSibling
from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.utils import WaitFillViewStrategy
from widgetastic.widget import Checkbox
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Select
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly import Button
from widgetastic_patternfly import Input

from mta.base.application.implementations.web_ui import MTANavigateStep
from mta.base.application.implementations.web_ui import navigate_to
from mta.base.application.implementations.web_ui import ViaWebUI
from mta.base.modeling import BaseCollection
from mta.base.modeling import BaseEntity
from mta.entities import AllProjectView
from mta.entities.analysis_results import AnalysisResultsView
from mta.utils import conf
from mta.utils.ftp import FTPClientWrapper
from mta.utils.update import Updateable
from mta.widgetastic import AddButton
from mta.widgetastic import HiddenFileInput
from mta.widgetastic import ProjectSteps
from mta.widgetastic import TransformationPath


class AddProjectView(AllProjectView):
    fill_strategy = WaitFillViewStrategy("15s")

    @View.nested
    class create_project(View):  # noqa
        create_project = ProjectSteps("Create Project")
        name = Input(name="projectTitle")
        description = Input(locator='.//textarea[@id="idDescription"]')
        next_button = Button("Next")
        cancel_button = Button("Cancel")
        fill_strategy = WaitFillViewStrategy("20s")

        @property
        def is_displayed(self):
            return self.name.is_displayed and self.create_project.is_displayed

        def after_fill(self, was_change):
            self.next_button.click()

    @View.nested
    class add_applications(View):  # noqa
        add_applications = ProjectSteps("Add Applications")
        delete_application = Text(locator=".//div[contains(@class, 'action-button')]/span/i")
        confirm_delete = Button("Yes")
        upload_file = HiddenFileInput(id="fileUpload")
        next_button = Button("Next")
        back_button = Button("Back")
        cancel_button = Button("Cancel")
        fill_strategy = WaitFillViewStrategy("20s")

        @property
        def is_displayed(self):
            return self.add_applications.is_displayed

        def fill(self, values):
            app_list = values.get("app_list")
            env = conf.get_config("env")
            fs = FTPClientWrapper(env.ftpserver.entities.mta)
            for app in app_list:
                # Download application file to analyze
                # This part has to be here as file is downloaded temporarily
                file_path = fs.download(app)
                self.upload_file.fill(file_path)
            wait_for(lambda: self.next_button.is_enabled, delay=0.2, timeout=60)
            was_change = True
            self.after_fill(was_change)
            return was_change

        def after_fill(self, was_change):
            self.next_button.click()

    class configure_analysis(View):  # noqa
        PARAMETERS = ("pkg",)
        configure_analysis = ProjectSteps("Configure the Analysis")
        transformation_path = TransformationPath()
        application_packages = Text(
            locator=".//wu-select-packages/h3[normalize-space(.)='Application packages']"
        )
        save_and_run = Button("Save & Run")
        yes_button = Button("Yes")
        fill_strategy = WaitFillViewStrategy("15s")

        @property
        def is_displayed(self):
            return self.configure_analysis.is_displayed

        @ParametrizedView.nested
        class application_package(ParametrizedView):  # noqa
            PARAMETERS = ("pkg",)

            app_checkbox = Text(
                ParametrizedLocator(".//span[text()[normalize-space(.)={pkg|quote}]]")
            )
            include_pkg = Text(
                ParametrizedLocator(
                    ".//div[./preceding-sibling::div"
                    "/h2[text()[normalize-space()='Include packages']]]"
                    "/select/option[text()[normalize-space()={pkg|quote}]]"
                )
            )

            exclude_pkg = Text(
                ParametrizedLocator(
                    ".//div[./preceding-sibling::div/"
                    "h2[text()[normalize-space()='Exclude packages']]]"
                    "/select/option[text()[normalize-space()={pkg|quote}]]"
                )
            )

            @property
            def is_displayed(self):
                return self.app_checkbox.is_displayed and self.include_pkg.is_displayed

        @View.nested
        class use_custom_rules(View):  # noqa
            expand_custom_rules = Text(
                locator=".//span[contains(@class ,'fa field-selection-toggle-pf')]"
            )
            add_button = Button("Add")
            upload_file = HiddenFileInput(id="fileUpload")
            add_rules_button = AddButton("Add")
            select_all_rules = Checkbox(locator=".//input[@title='Select All Rows']")
            rule = Text(
                locator=".//option[text()[normalize-space()='custom.Test1rules.rhamt.xml']]"
            )

        @View.nested
        class use_custom_labels(View):  # noqa
            expand_custom_labels = Text(
                locator=".//a[text()[normalize-space(.)='Use custom labels']]"
            )
            add_button = Button("Add")
            upload_file = HiddenFileInput(id="fileUpload")
            add_labels_button = AddButton("Add")
            select_all_labels = Checkbox(locator=".//input[@value='allRowsSelected']")
            label = Text(
                locator=".//option[text()[normalize-space()='customWebLogic.windup.label.xml']]"
            )

        @View.nested
        class advanced_options(View):  # noqa
            expand_advanced_options = Text(
                locator=".//a[text()[normalize-space(.)='Advanced options']]"
            )
            add_option_button = Button("Add option")
            option_select = Select(name="newOptionTypeSelection")
            select_value = Checkbox(locator=".//input[@name='currentOptionInput']")
            add_button = Button("Add")
            cancel_button = Button("Cancel")
            delete_button = Button("Delete")

        def fill(self, values):
            """
            Args:
                values:
            """
            if values.get("transformation_path"):
                self.transformation_path.select_card(card_name=values.get("transformation_path"))
            if not platform == "win32":
                wait_for(lambda: self.application_packages.is_displayed, delay=0.6, timeout=500)
            was_change = True
            self.after_fill(was_change)
            return was_change

        def after_fill(self, was_change):
            self.save_and_run.click()
            if self.yes_button.is_displayed:
                self.yes_button.click()

    @property
    def is_displayed(self):
        return (
            self.create_project.is_displayed
            or self.add_applications.is_displayed
            or self.configure_analysis.is_displayed
        )


class DetailsProjectView(AllProjectView):
    run_analysis_button = Button("Run Analysis")
    title = Text(locator=".//div/h2[normalize-space(.)='Active Analysis']")

    @property
    def is_displayed(self):
        return self.run_analysis_button.is_displayed and self.title.is_displayed


class EditProjectView(AllProjectView):
    title = Text(locator=".//div/h1[normalize-space(.)='Edit Project']")
    name = Input(name="projectTitle")
    description = Input(locator='.//textarea[@id="idDescription"]')
    update_project_button = Button("Update Project")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.update_project_button.is_displayed and self.title.is_displayed


class DeleteProjectView(AllProjectView):
    title = Text(
        locator=".//div[contains(@class, 'modal-header')]"
        "/h1[normalize-space(.)='Confirm Project Deletion']"
    )
    delete_project_name = Input(id="resource-to-delete")

    delete_button = Button("Delete")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.delete_button.is_displayed and self.title.is_displayed


@attr.s
class Project(BaseEntity, Updateable):

    name = attr.ib()
    description = attr.ib(default=None)
    app_list = attr.ib(default=None)
    transformation_path = attr.ib(default=None)

    @property
    def exists(self):
        """Check project exist or not"""
        view = navigate_to(self.parent, "All")
        return False if view.is_empty else self.name in view.projects.items

    def update(self, updates):
        view = navigate_to(self, "Edit")
        view.wait_displayed()
        changed = view.fill(updates)
        if changed:
            view.update_project_button.click()
        else:
            view.cancel_button.click()
        view = self.create_view(AllProjectView, override=updates)
        view.wait_displayed()
        assert view.is_displayed

    def delete(self, cancel=False, wait=False):
        """
        Args:
            cancel: cancel deletion
            wait: wait for delete
        """
        view = navigate_to(self, "Delete")
        view.fill({"delete_project_name": self.name})

        if cancel:
            view.cancel_button.click()
        else:
            view.delete_button.click()
            if wait:
                wait_for(lambda: not self.exists, delay=5, timeout=30)


@attr.s
class ProjectCollection(BaseCollection):

    ENTITY = Project

    def all(self):
        """Return all projects instance of Project class"""
        view = navigate_to(self, "All")
        if view.is_empty:
            return []
        else:
            return [
                self.instantiate(name=p.name, description=p.description)
                for p in view.projects.projects
            ]

    def create(self, name, description=None, app_list=None, transformation_path=None):
        """Create a new project.

        Args:
            name: The name of the project
            description: The description of the project
            app_list: Applications to be analyzed
            transformation_path: transformation_path
        """
        view = navigate_to(self, "Add")
        view.create_project.fill({"name": name, "description": description})
        view.add_applications.wait_displayed()
        view.add_applications.fill({"app_list": app_list})
        view.configure_analysis.wait_displayed()
        view.configure_analysis.fill({"transformation_path": transformation_path})

        project = self.instantiate(
            name=name,
            description=description,
            app_list=app_list,
            transformation_path=transformation_path,
        )
        view = self.create_view(AnalysisResultsView)
        view.wait_displayed("60s")
        assert view.is_displayed
        if platform == "win32":
            view.browser.refresh()
        wait_for(lambda: view.analysis_results.in_progress(), delay=0.2, timeout=450)
        wait_for(lambda: view.analysis_results.is_analysis_complete(), delay=0.2, timeout=450)
        assert view.analysis_results.is_analysis_complete()
        return project

    def sort_projects(self, criteria):
        view = navigate_to(self, "All")
        view.sort.item_select(criteria)

    def search_project(self, project):
        view = navigate_to(self, "All")
        view.search.fill(project)


@ViaWebUI.register_destination_for(ProjectCollection)
class All(MTANavigateStep):
    VIEW = AllProjectView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self, *args, **kwargs):
        if not self.prerequisite_view.is_empty:
            self.prerequisite_view.home_navigation.select("Projects")


@ViaWebUI.register_destination_for(ProjectCollection)
class Add(MTANavigateStep):
    VIEW = AddProjectView
    prerequisite = NavigateToSibling("All")

    def step(self, *args, **kwargs):
        if self.prerequisite_view.is_empty:
            self.prerequisite_view.blank_state.new_project_button.click()
        else:
            self.prerequisite_view.new_project_button.click()


@ViaWebUI.register_destination_for(Project)
class Edit(MTANavigateStep):
    VIEW = EditProjectView
    prerequisite = NavigateToAttribute("parent", "All")

    def step(self, *args, **kwargs):
        proj = self.prerequisite_view.projects.get_project(self.obj.name)
        proj.edit()


@ViaWebUI.register_destination_for(Project)
class Delete(MTANavigateStep):
    VIEW = DeleteProjectView
    prerequisite = NavigateToAttribute("parent", "All")

    def step(self, *args, **kwargs):
        proj = self.prerequisite_view.projects.get_project(self.obj.name)
        proj.delete()
