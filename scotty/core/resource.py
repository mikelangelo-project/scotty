import logging
import imp
import contextlib
import os
import sys

import scotty.core.checkout

logger = logging.getLogger(__name__)

class ModuleLoader(object):
    def __init__(self, parent_module, default_name):
        self.parent_module = parent_module
        self.default_name = default_name

    def load_by_path(self, path, name=None):
        name = name or self.default_name
        name = "{parent}.{name}".format(parent=self._parent_module.__name__, name=name)
        self.add_syspath(path)
        module_ = imp.load_source(name, path)
        return module_

    @property
    def parent_module(self):
        return self._parent_module

    @parent_module.setter
    def parent_module(self, name):
        self._parent_module = sys.modules.setdefault(name, imp.new_module(name))
        self._parent_module.__file__ = '<virtual {}>'.format(name)

    def add_syspath(self, path):
        path = os.path.dirname(os.path.abspath(path))
        sys.path.insert(0, path)


class Resource(object):
    def __init__(self):
        self.config = None
        self.workspace = None
        self.module = None

    @property
    def name(self):
        return self.config['name']


class Workspace(object):
    def __init__(self, path):
        self.path = path

    @contextlib.contextmanager
    def cwd(self):
        prev_cwd = os.getcwd()
        os.chdir(self.path)
        yield
        os.chdir(prev_cwd)


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self._checkout_manager = scotty.core.checkout.Manager()
        self._module_loader = ModuleLoader('scotty.component.resource__gen', 'anonymous_resource')
        self.resource = None

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
