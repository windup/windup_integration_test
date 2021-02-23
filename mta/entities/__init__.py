import attr
import importscan
import sentaku
from mta.base.modeling import BaseEntity


@attr.s
class Server(BaseEntity, sentaku.modeling.ElementMixin):
    logged_in = sentaku.ContextualMethod()

    def __init__(self, application, name=None, name_base=None, description=None, vm_name=None):
        self.application = application
        self.parent = self.appliance.context

from mta.entities import webui, operator_ui  # NOQA last for import cycles
importscan.scan(webui)
importscan.scan(operator_ui)