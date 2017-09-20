import logging
import imp
import os
import sys
import uuid

logger = logging.getLogger(__name__)


class ModuleLoader(object):
    @classmethod
    def load_by_path(cls, path, name, parent_module_name):
        parent_module = cls.create_parent_module(parent_module_name)
        uuid_hex = uuid.uuid4().hex[:8]
        name = name or 'anonymous_component'
        name = "{}.{}_{}".format(parent_module.__name__, uuid_hex, name)
        cls.add_syspath(path)
        module_ = imp.load_source(name, path)
        return module_

    @classmethod
    def load_by_component(cls, component):
        module_ = cls.load_by_path(
            component.module_path,
            component.name,
            component.parent_module_name)
        return module_

    @classmethod
    def create_parent_module(cls, parent_module_name):
        parent_module = sys.modules.setdefault(
            parent_module_name,
            imp.new_module(parent_module_name))
        parent_module.__file__ = '<virtual {}>'.format(parent_module_name)
        return parent_module

    @classmethod
    def add_syspath(cls, path):
        path = os.path.dirname(os.path.abspath(path))
        sys.path.insert(0, path)
