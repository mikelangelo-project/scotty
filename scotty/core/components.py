import logging
import os
import sys

from scotty.core.context import ContextAccessible
from scotty.core.exceptions import ExperimentException

logger = logging.getLogger(__name__)


class Component(object):
    def __init__(self):
        self.config = None
        self.workspace = None
        self._setaccess('config')
        self._setaccess('name')

    def _setaccess(self, parameter):
        ContextAccessible(self.__class__.__name__).setaccess(parameter)

    @property
    def name(self):
        return self.config['name']

    def issource(self, type_):
        source = self.config['generator'].split(':')
        source_type = source[0].upper()
        same_type = source_type == type_.upper()
        return same_type

    def isinstance(self, type_str):
        class_ = getattr(sys.modules[__name__], type_str)
        return isinstance(self, class_)

    @property
    def type(self):
        type_ = self.__class__.__name__
        return type_.lower()


class Workload(Component):
    def __init__(self):
        super(Workload, self).__init__()
        self.module = None
        self.parent_module_name = 'scotty.workload_gen'
        self._setaccess('params')
        self._setaccess('resources')

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'workload_gen.py')
   
    @property
    def params(self):
        return self.config['params']

    @property
    def resources(self):
        return self.config['resources']


class Experiment(Component):
    def __init__(self):
        super(Experiment, self).__init__()
        self.workloads = {}
        self.resources = {}

    def add_component(self, component):
        if component.isinstance('Workload'):
            self.workloads[component.name] = component
        elif component.isinstance('Resource'):
            self.resources[component.name] = component
        else:
            raise ExperimentException(
                'Component {} can not added to experiment'.format(component.type))


class Resource(Component):
    def __init__(self):
        super(Resource, self).__init__()
        self.module = None
        self.parent_module_name = 'scotty.resource_gen'
        self.endpoint = None
        self._setaccess('params')
        self._setaccess('endpoint')

    @property
    def params(self):
        return self.config['params']

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'resource_gen.py')
