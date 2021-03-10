import attr
from taretto.navigate import NavigateToAttribute
from taretto.navigate import NavigateToSibling
from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.utils import WaitFillViewStrategy
from widgetastic.widget import ParametrizedView
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly4 import Button

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
from mta.widgetastic import HiddenFileInput
from mta.widgetastic import Input
from mta.widgetastic import MTASelect
from mta.widgetastic import TransformationPath


class AddProjectView(AllProjectView):
    fill_strategy = WaitFillViewStrategy("15s")
    title = Text(locator=".//h1[normalize-space(.)='Create project']")

    @property
    def is_displayed(self):
        return self.title.is_displayed and self.create_project.is_displayed

    @View.nested
    class create_project(View):  # noqa
        title = Text(locator=".//h5[normalize-space(.)='Project details']")
        name = Input(name="name")
        description = Input(locator='.//textarea[@name="description"]')
        next_button = Button("Next")
        cancel_button = Button("Cancel")
        yes_button = Button("Yes")
        no_button = Button("No")
        fill_strategy = WaitFillViewStrategy("30s")

        @property
        def is_displayed(self):
            return self.name.is_displayed and self.title.is_displayed

        def after_fill(self, was_change):
            self.next_button.click()

    @View.nested
    class add_applications(View):  # noqa
        title = Text(locator=".//h5[normalize-space(.)='Add applications']")
        delete_application = Text(locator=".//button[contains(@aria-label, 'delete-application')]")
        browse_button = Button("Browse")
        upload_file = HiddenFileInput(
            locator='.//input[@accept=".ear, .har, .jar, .rar, .sar, .war, .zip"]'
        )

        next_button = Button("Next")
        back_button = Button("Back")
        cancel_button = Button("Cancel")
        fill_strategy = WaitFillViewStrategy("20s")

        @property
        def is_displayed(self):
            return self.title.is_displayed and self.browse_button.is_displayed

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
        @View.nested
        class set_transformation_target(View):  # noqa
            title = Text(locator=".//h5[normalize-space(.)='Select transformation target']")
            transformation_path = TransformationPath()
            application_packages = Text(
                locator=".//wu-select-packages/h3[normalize-space(.)='Application packages']"
            )
            next_button = Button("Next")
            back_button = Button("Back")
            cancel_button = Button("Cancel")
            fill_strategy = WaitFillViewStrategy("15s")

            @property
            def is_displayed(self):
                return self.title.is_displayed and self.transformation_path.is_displayed

            def fill(self, values):
                """
                Args:
                    values: transformation path to be selected
                """
                if values.get("transformation_path"):
                    self.transformation_path.select_card(
                        card_name=values.get("transformation_path")
                    )
                was_change = True
                wait_for(lambda: self.next_button.is_enabled, delay=0.2, timeout=60)
                self.after_fill(was_change)
                return was_change

            def after_fill(self, was_change):
                self.next_button.click()

        @ParametrizedView.nested
        class select_packages(ParametrizedView):  # noqa
            title = Text(locator=".//h5[normalize-space(.)='Select packages']")
            PARAMETERS = ("pkg",)
            select_all_packages = Text(locator=".//input[@class='ant-checkbox-input']")

            packages = Text(
                ParametrizedLocator(
                    ".//div[contains(@class, 'ant-tree-treenode-switcher-close') "
                    "and not(contains(@class, 'ant-tree-treenode-disabled'))]"
                    "/span/span/span[normalize-space(.)={pkg|quote}]"
                )
            )
            included_packages = Text(
                ParametrizedLocator(
                    ".//li[@class='ant-transfer-list-content-item']"
                    "/span[normalize-space(.)={pkg|quote}]"
                )
            )
            move_into_button = Button(locator=".//span[contains(@class, 'anticon anticon-right')]")
            move_from_button = Button(locator=".//span[contains(@class, 'anticon anticon-left')]")

            next_button = Button("Next")
            back_button = Button("Back")
            cancel_button = Button("Cancel")
            fill_strategy = WaitFillViewStrategy("15s")

            @property
            def is_displayed(self):
                return self.title.is_displayed and self.select_all_packages.is_displayed

            def fill_pkg(self):
                """ Add packages """
                self.packages.click()
                self.move_into_button.click()
                was_change = True
                return was_change

            def remove(self):
                """ Remove packages"""
                self.included_packages.click()
                self.move_from_button.click()
                was_change = True
                return was_change

            def fill(self, values):
                """
                Args:
                    values: application packages to be selected
                """
                if values.get("pkg"):
                    self.fill_pkg()
                was_change = True
                self.after_fill(was_change)
                return was_change

            def after_fill(self, was_change):
                self.next_button.click()

    class advanced(View):  # noqa
        @View.nested
        class custom_rules(View):  # noqa
            title = Text(locator=".//h5[normalize-space(.)='Custom rules']")
            add_rule_button = Button("Add rule")
            upload_rule = HiddenFileInput(locator='.//input[contains(@accept,".xml")]')
            close_button = Button("Close")
            enabled_button = Text(locator=".//label/span[contains(@class, 'pf-c-switch__toggle')]")
            next_button = Button("Next")
            back_button = Button("Back")
            cancel_button = Button("Cancel")
            fill_strategy = WaitFillViewStrategy("15s")

            @property
            def is_displayed(self):
                return self.title.is_displayed and self.add_rule_button.is_displayed

            def fill(self, values):
                """
                Args:
                    values: custom rule file to be uploaded
                """
                if values.get("file_rule"):
                    self.expand_custom_rules.click()
                was_change = True
                wait_for(lambda: self.next_button.is_enabled, delay=0.2, timeout=60)
                self.after_fill(was_change)
                return was_change

            def after_fill(self, was_change):
                self.next_button.click()

        @View.nested
        class custom_labels(View):  # noqa
            title = Text(locator=".//h5[normalize-space(.)='Custom labels']")
            add_label_button = Button("Add label")
            upload_label = HiddenFileInput(locator='.//input[contains(@accept,".xml")]')
            enabled_button = Text(locator=".//label/span[contains(@class, 'pf-c-switch__toggle')]")
            close_button = Button("Close")
            next_button = Button("Next")
            back_button = Button("Back")
            cancel_button = Button("Cancel")
            fill_strategy = WaitFillViewStrategy("15s")

            @property
            def is_displayed(self):
                return self.title.is_displayed and self.add_label_button.is_displayed

            def fill(self, values):
                """
                Args:
                    values: custom label file to be uploaded
                """
                if values.get("file_label"):
                    self.expand_custom_labels.click()
                wait_for(lambda: self.next_button.is_enabled, delay=0.2, timeout=60)
                was_change = True
                self.after_fill(was_change)
                return was_change

            def after_fill(self, was_change):
                self.next_button.click()

        @View.nested
        class options(View):  # noqa
            title = Text(locator=".//h5[normalize-space(.)='Advanced options']")
            select_target = MTASelect(
                locator='.//div/input[contains(@placeholder, "Select targets")]'
                '/ancestor::div[contains(@class, "pf-c-select")]'
            )
            select_source = MTASelect(
                locator='.//div/input[contains(@placeholder, "Select sources")]'
                '/ancestor::div[contains(@class, "pf-c-select")]'
            )

            export_csv = Text(
                locator=".//span[./preceding-sibling::input[@aria-label='Export CSV']]"
            )
            disable_tattletale = Text(
                locator=".//span[./preceding-sibling::input[@aria-label='Disable Tattletale']]"
            )
            class_not_found_analysis = Text(
                locator=".//span[./preceding-sibling::input"
                "[@aria-label='Class Not Found analysis']]"
            )
            compatible_files_report = Text(
                locator=".//span[./preceding-sibling::input"
                "[@aria-label='Compatible Files report']]"
            )
            exploded_app = Text(
                locator=".//span[./preceding-sibling::input[@aria-label='Exploded app']]"
            )
            keep_work_dirs = Text(
                locator=".//span[./preceding-sibling::input[@aria-label='Keep work dirs']]"
            )
            skip_reports = Text(
                locator=".//span[./preceding-sibling::input[@aria-label='Skip reports']]"
            )
            allow_network_access = Text(
                locator=".//span[./preceding-sibling::input[@aria-label='Allow network access']]"
            )
            mavenize = Text(locator=".//span[./preceding-sibling::input[@aria-label='Mavenize']]")
            source_mode = Text(
                locator=".//span[./preceding-sibling::input[@aria-label='Source mode']]"
            )

            add_button = Button("Add")
            cancel_button = Button("Cancel")
            next_button = Button("Next")
            back_button = Button("Back")
            fill_strategy = WaitFillViewStrategy("25s")

            @property
            def is_displayed(self):
                return self.title.is_displayed and self.select_target.is_displayed

            def after_fill(self, was_change):
                self.next_button.click()

    @View.nested
    class review(View):  # noqa
        title = Text(locator=".//h5[normalize-space(.)='Review project details']")
        save = Button("Save")
        save_and_run = Button("Save and run")
        fill_strategy = WaitFillViewStrategy("15s")

        @property
        def is_displayed(self):
            return self.title.is_displayed and self.save_and_run.is_displayed

        def after_fill(self, was_change):
            wait_for(lambda: self.save_and_run.is_enabled, delay=5, timeout=30)
            self.save_and_run.click()


class DetailsProjectView(AllProjectView):
    run_analysis_button = Button("Run Analysis")
    title = Text(locator=".//div/h2[normalize-space(.)='Active Analysis']")

    @property
    def is_displayed(self):
        return self.run_analysis_button.is_displayed and self.title.is_displayed


class EditProjectView(AllProjectView):
    title = Text(locator=".//h1[normalize-space(.)='Project details']")
    name = Input(name="name")
    description = Input(name="description")
    save_button = Button("Save")
    cancel_button = Button("Cancel")
    fill_strategy = WaitFillViewStrategy("35s")

    @property
    def is_displayed(self):
        return self.save_button.is_displayed and self.title.is_displayed


class DeleteProjectView(AllProjectView):
    title = Text(locator=".//h1[normalize-space(.)='Project details']")
    delete_project_name = Input(id="matchText")
    fill_strategy = WaitFillViewStrategy("35s")

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
        view.table.wait_displayed("20s")
        for row in view.table:
            if row.name.text == self.name:
                return True
        return False

    def update(self, updates):
        view = navigate_to(self, "Edit")
        view.wait_displayed("30s")
        changed = view.fill(updates)
        if changed:
            view.save_button.click()
        else:
            view.cancel_button.click()
        view = self.create_view(AllProjectView, override=updates)
        view.wait_displayed("40s")
        assert view.is_displayed

    def delete(self, cancel=False, wait=False):
        """
        Args:
            cancel: cancel deletion
            wait: wait for delete
        """
        view = navigate_to(self, "Delete")
        view.wait_displayed("30s")
        view.fill({"delete_project_name": self.name})
        if cancel:
            view.cancel_button.click()
        else:
            wait_for(lambda: view.delete_button.is_enabled, delay=5, timeout=30)
            view.delete_button.click()
            if wait:
                wait_for(lambda: not self.exists, delay=5, timeout=30)

    def delete_if_exists(self):
        """Check project exist and delete"""
        if self.exists:
            self.delete()


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
                self.instantiate(name=p.name.text, description=p.description.text)
                for p in view.all_projects
            ]

    def create(
        self,
        name,
        description=None,
        app_list=None,
        transformation_path=None,
        pkg=None,
        file_rule=None,
        file_label=None,
        options=None,
    ):
        """Create a new project.

        Args:
            name: The name of the project
            description: The description of the project
            app_list: Applications to be analyzed
            transformation_path: transformation_path
            pkg: package
            file_rule: Rules
            file_label: Label
            options: Options
        """
        view = navigate_to(self, "Add")
        view.create_project.fill({"name": name, "description": description})
        view.add_applications.wait_displayed()
        view.add_applications.fill({"app_list": app_list})
        view.configure_analysis.set_transformation_target.wait_displayed()
        view.configure_analysis.set_transformation_target.fill(
            {"transformation_path": transformation_path}
        )
        wait_for(
            lambda: view.configure_analysis.select_packages(pkg).is_displayed, delay=0.2, timeout=60
        )
        view.configure_analysis.select_packages(pkg).wait_displayed()
        view.configure_analysis.select_packages(pkg).fill({"pkg": pkg})
        view.advanced.custom_rules.wait_displayed()
        view.advanced.custom_rules.fill({"file_rule": file_rule})
        view.advanced.custom_labels.wait_displayed()
        view.advanced.custom_labels.fill({"file_label": file_label})
        view.advanced.options.wait_displayed()
        view.advanced.options.fill({"options": options})
        view.review.wait_displayed("30s")
        view.review.after_fill(was_change=True)

        project = self.instantiate(
            name=name,
            description=description,
            app_list=app_list,
            transformation_path=transformation_path,
        )
        view = self.create_view(AnalysisResultsView)
        view.wait_displayed("60s")
        assert view.is_displayed
        wait_for(lambda: view.analysis_results.in_progress(), delay=0.2, timeout=450)
        wait_for(lambda: view.analysis_results.is_analysis_complete(), delay=0.2, timeout=450)
        assert view.analysis_results.is_analysis_complete()
        return project

    def sort_projects(self, criteria, order):
        view = navigate_to(self, "All")
        view.table.sort_by(criteria, order)

    def search_project(self, project):
        view = navigate_to(self, "All")
        view.search.fill(project)

    def get_project(self, name):
        view = navigate_to(self, "All")
        for row in view.table:
            if row.name.text == name:
                return row


@ViaWebUI.register_destination_for(ProjectCollection)
class All(MTANavigateStep):
    VIEW = AllProjectView
    prerequisite = NavigateToAttribute("application.collections.base", "LoggedIn")

    def step(self, *args, **kwargs):
        self.prerequisite_view.wait_displayed("20s")
        if not self.prerequisite_view.is_empty:
            self.prerequisite_view.navigation.select("Projects")


@ViaWebUI.register_destination_for(ProjectCollection)
class Add(MTANavigateStep):
    VIEW = AddProjectView
    prerequisite = NavigateToSibling("All")

    def step(self, *args, **kwargs):
        self.prerequisite_view.wait_displayed("20s")
        if self.prerequisite_view.is_empty:
            self.prerequisite_view.blank_state.create_project.click()
        else:
            self.prerequisite_view.create_project.click()


@ViaWebUI.register_destination_for(Project)
class Edit(MTANavigateStep):
    VIEW = EditProjectView
    prerequisite = NavigateToAttribute("parent", "All")

    def step(self, *args, **kwargs):
        for row in self.prerequisite_view.table:
            if row.name.text == self.obj.name:
                row[self.prerequisite_view.ACTIONS_INDEX].widget.item_select("Edit")


@ViaWebUI.register_destination_for(Project)
class Delete(MTANavigateStep):
    VIEW = DeleteProjectView
    prerequisite = NavigateToAttribute("parent", "All")

    def step(self, *args, **kwargs):
        for row in self.prerequisite_view.table:
            if row.name.text == self.obj.name:
                row[self.prerequisite_view.ACTIONS_INDEX].widget.item_select("Delete")
