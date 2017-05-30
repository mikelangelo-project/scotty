import logging
import imp
import contextlib
import os
import sys

from scotty.config import ScottyConfig
from scotty.core.checkout import CheckoutManager
from scotty.core.moduleloader import ModuleLoader
from scotty.core.workspace import Workspace
from scotty.core.components import Resource

logger = logging.getLogger(__name__)


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self._checkout_manager = CheckoutManager()
        self._module_loader = ModuleLoader('scotty.component.resource__gen', 'anonymous_resource')
        self.resource = None
        self._scotty_config = ScottyConfig()

    def deploy(self):
        self._prepare()
        self._checkout()
        self._load()
        self._deploy()

    def _prepare(self):
        if not self.resource:
            self.resource = Resource()
        if not self.resource.workspace:
            path = os.path.abspath(self._options.workspace)
            self.resource.workspace = Workspace(path)

    def _checkout(self):
        if self._options.skip_checkout:
            return

    def _load(self):
        pass

    def _deploy(self):
        if not self._options.mock:
            pass
