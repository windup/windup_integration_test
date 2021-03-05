import importscan

from mta.base.application.implementations.web_ui import ViaWebUI
from mta.utils import conf


class Application(object):
    def __init__(
        self, hostname=None, ocphostname=None, user=None, password=None, *, config=None,
    ):
        self.config = config or conf.get_config("env")
        # Set up hostnames/paths
        self.hostname = hostname or self.config.application.hostname
        self.ocphostname = ocphostname or self.config.application.ocphostname
        self.user = user or self.config.application.user
        self.password = password or self.config.application.password
        self.web_ui = ViaWebUI(owner=self)
        self.mta_context = "ViaWebUI"
        from mta.base.application.implementations import MTAImplementationContext

        # TODO: include other context in future
        self.context = MTAImplementationContext.from_instances([self.web_ui])
        #    [self.browser])

    @classmethod
    def from_testcontext(cls, context):
        """given a entity, pytest item or pytest configuration,

        find the contextually belonging application and return it

        .. code:: python

            def pytest_generate_tests(metafunc):
                if is_marked_for_interesting_parameterization(metafunc.definition):
                    app = Application.from_testcontext(metafunc.definition)
                    parameterize_overly_interestingly(metafunc, app)


            def myhelper(advisor_issue):
                app = Application.from_testcontext(advisor_issue)
                app.advisor.fun_heler_i_pulled_out_of_my_nose(advisor_issue)

        """
        pass
        # from iqe.test_framework.helpers import find_application
        #
        # return find_application(context)

    @property
    def application(self):
        return self

    @property
    def collections(self):
        from mta.base.modeling import EntityCollections

        return EntityCollections.for_application(self)

    # @contextmanager
    # def copy_using(self, *, user):
    #     """
    #     returns a teporary application with changes applied
    #
    #     :param user: a user credential record to use instead of the  default/original one
    #     """
    #     with _application_construction_allowed():
    #         app = Application(config=self.config, user=user)
    #     yield app
    #     app.web_ui.browser_manager.close()


from mta import base  # noqa

importscan.scan(base)
