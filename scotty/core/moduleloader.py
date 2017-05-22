import logging
import imp
import os
import sys

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
