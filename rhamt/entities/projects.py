import attr
from taretto.navigate import NavigateToAttribute
from taretto.navigate import NavigateToSibling
from widgetastic.utils import WaitFillViewStrategy
from widgetastic.widget import FileInput
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly import Button
from widgetastic_patternfly import Input

from rhamt.base.application.implementations.web_ui import navigate_to
from rhamt.base.application.implementations.web_ui import RhamtNavigateStep
from rhamt.base.application.implementations.web_ui import ViaWebUI
from rhamt.base.modeling import BaseCollection
from rhamt.base.modeling import BaseEntity
from rhamt.entities import BaseLoggedInPage
from rhamt.entities.analysis_results import AnalysisResultsView
from rhamt.utils import conf
from rhamt.utils.ftp import FTPClientWrapper
from rhamt.utils.update import Updateable
from rhamt.utils.wait import TimedOutError
from wait_for import wait_for
from rhamt.widgetastic import ProjectList
from rhamt.widgetastic import ProjectSteps
from rhamt.widgetastic import TransformationPath


class AllProjectView(BaseLoggedInPage):
    project_list = ProjectList("projects-list")
    new_project_button = Button("New Project")
    project = Text(
        locator=".//div[contains(@class, 'projects-bar')]/h1[normalize-space(.)='Projects']"
    )

    @property
    def is_displayed(self):
        return self.new_project_button.is_displayed and self.project.is_displayed


class AddProjectView(AllProjectView):
    fill_strategy = WaitFillViewStrategy("15s")

    @View.nested
    class create_project(View):  # noqa
        create_project = ProjectSteps("Create Project")
        name = Input(name="projectTitle")
        description = Input(locator='.//textarea[@id="idDescription"]')
        next_btn = Button("Next")
        cancel_btn = Button("Cancel")
        fill_strategy = WaitFillViewStrategy("15s")

        @property
        def is_displayed(self):
            return self.name.is_displayed and self.create_project.is_displayed

        def after_fill(self, was_change):
            self.next_btn.click()

    @View.nested
    class add_applications(View):  # noqa
        add_applications = ProjectSteps("Add Applications")
        delete_application = Text(locator=".//div[contains(@class, 'action-button')]/span/i")
        confirm_delete = Button("Yes")
        upload_file = FileInput(id="fileUpload")
        next_btn = Button("Next")
        fill_strategy = WaitFillViewStrategy("20s")

        @property
        def is_displayed(self):
            return self.upload_file.is_displayed and self.add_applications.is_displayed

        def fill(self, values):
            app_list = values.get('app_list')
            env = conf.get_config("env")
            fs = FTPClientWrapper(env.ftpserver.entities.rhamt)
            for app in app_list:
                # Download application file to analyze
                # This part has to be here as file is downloaded temporarily
                file_path = fs.download(app)
                self.upload_file.fill(file_path)
            wait_for(lambda: self.next_btn.is_enabled, delay=0.2, timeout=60)
            was_change = True
            self.after_fill(was_change)
            return was_change

        def after_fill(self, was_change):
            self.next_btn.click()

    @View.nested
    class configure_analysis(View):  # noqa
        configure_analysis = ProjectSteps("Configure the Analysis")
        transformation_path = TransformationPath()
        application_packages = Text(
            locator=".//wu-select-packages/h3[normalize-space(.)='Application packages']"
        )
        save_and_run = Button("Save & Run")
        fill_strategy = WaitFillViewStrategy("15s")

        @property
        def is_displayed(self):
            return self.configure_analysis.is_displayed

        def fill(self, values):
            """
            Args:
                values:
            """
            if values.get("transformation_path"):
                self.transformation_path.select_card(card_name=values.get("transformation_path"))
            wait_for(lambda: self.application_packages.is_displayed, delay=0.6, timeout=240)
            was_change = True
            self.after_fill(was_change)
            return was_change

        def after_fill(self, was_change):
            self.save_and_run.click()


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
    update_project_btn = Button("Update Project")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.update_project_btn.is_displayed and self.title.is_displayed


class DeleteProjectView(AllProjectView):
    title = Text(locator=".//div[contains(@class, 'modal-header')]"
                         "/h1[normalize-space(.)='Confirm Project Deletion']")
    delete_project_name = Input(id="resource-to-delete")
    delete_btn = Button("Delete")
    cancel_button = Button("Cancel")

    @property
    def is_displayed(self):
        return self.delete_btn.is_displayed and self.title.is_displayed


@attr.s
class Project(BaseEntity, Updateable):

    name = attr.ib()
    description = attr.ib()
    app_list = attr.ib(default=None)
    transformation_path = attr.ib(default=None)

    def exists(self, project_name):
        view = navigate_to(self.parent, "All")
        return view.project_list.exists(project_name)

    def update(self, updates):
        view = navigate_to(self, "Edit")
        changed = view.fill(updates)
        if changed:
            view.update_project_btn.click()
        else:
            view.cancel_button.click()
        view = self.create_view(AllProjectView, override=updates)
        view.wait_displayed()
        assert view.is_displayed

    def delete(self, project_name):
        view = navigate_to(self, "Delete")
        view.fill({'delete_project_name': project_name})
        view.delete_btn.click()
        import time
        time.sleep(10)


@attr.s
class ProjectCollection(BaseCollection):

    ENTITY = Project

    def create(self, name, description, app_list=None, transformation_path=None):
        """Create a catalog.

        Args:
            name: The name of the project
            description: The description of the project
            app_list: Applications to be analyzed
            transformation_path: transformation_path
        """
        view = navigate_to(self, "Add")
        view.create_project.fill({"name": name, "description": description})
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
        view.wait_displayed()
        assert view.is_displayed
        wait_for(lambda : view.analysis_results.in_progress(), delay=0.2, timeout=120)
        wait_for(lambda: view.analysis_results.is_analysis_complete(), delay=0.2, timeout=120)
        assert view.analysis_results.is_analysis_complete()
        return project


@ViaWebUI.register_destination_for(ProjectCollection)
class All(RhamtNavigateStep):
    VIEW = AllProjectView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self, *args, **kwargs):
        self.prerequisite_view.home_navigation.select("Projects")


@ViaWebUI.register_destination_for(ProjectCollection)
class Add(RhamtNavigateStep):
    VIEW = AddProjectView
    prerequisite = NavigateToSibling("All")

    def step(self, *args, **kwargs):
        self.prerequisite_view.new_project_button.click()


@ViaWebUI.register_destination_for(Project)
class Edit(RhamtNavigateStep):
    VIEW = EditProjectView
    prerequisite = NavigateToAttribute('parent', 'All')

    def step(self, *args, **kwargs):
        self.prerequisite_view.project_list.edit_project(self.obj.name)


@ViaWebUI.register_destination_for(Project)
class Delete(RhamtNavigateStep):
    VIEW = DeleteProjectView
    prerequisite = NavigateToAttribute('parent', 'All')

    def step(self, *args, **kwargs):
        self.prerequisite_view.project_list.delete_project(self.obj.name)
