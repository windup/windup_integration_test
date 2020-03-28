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
        fill_strategy = WaitFillViewStrategy("15s")

        @property
        def is_displayed(self):
            return self.name.is_displayed and self.create_project.is_displayed

        def after_fill(self, was_change):
            self.next_btn.click()

    @View.nested
    class add_applications(View):  # noqa
        add_applications = ProjectSteps("Add Applications")
        upload_file = FileInput(id="fileUpload")
        next_btn = Button("Next")
        fill_strategy = WaitFillViewStrategy("15s")

        @property
        def is_displayed(self):
            return self.upload_file.is_displayed and self.add_applications.is_displayed

        def fill(self, values):
            # Download application file to analyze
            # This part has to be here as file is downloaded temporarily
            env = conf.get_config("env")
            fs = FTPClientWrapper(env.ftpserver.entities.rhamt)
            file_path = fs.download(values.get("file_name"))

            self.upload_file.fill(file_path)
            self.next_btn.wait_displayed()
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
            self.transformation_path.select_card(card_name=values.get("transformation_path"))
            self.application_packages.wait_displayed()
            was_change = True
            self.after_fill(was_change)
            return was_change

        def after_fill(self, was_change):
            self.save_and_run.click()


@attr.s
class Project(BaseEntity):

    name = attr.ib()
    description = attr.ib()
    file_name = attr.ib(default=None)
    transformation_path = attr.ib(default="Application server migration to EAP")

    def exists(self, project_name):
        view = navigate_to(self.parent, "All")
        return project_name in view.project_list.read()


@attr.s
class ProjectCollection(BaseCollection):

    ENTITY = Project

    def create(self, name, description, file_name=None, transformation_path=None):
        """Create a catalog.

        Args:
            name: The name of the project
            description: The description of the project
            file_name: Application to be analyzed
            transformation_path: transformation_path
        """
        view = navigate_to(self, "Add")
        view.create_project.fill({"name": name, "description": description})
        view.add_applications.fill({"file_name": file_name})

        view.configure_analysis.wait_displayed()
        view.configure_analysis.fill({"transformation_path": transformation_path})

        project = self.instantiate(
            name=name,
            description=description,
            file_name=file_name,
            transformation_path=transformation_path,
        )
        view = self.create_view(AnalysisResultsView)
        view.wait_displayed()
        assert view.is_displayed
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
