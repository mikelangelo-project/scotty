import logging
import os
import sys


logger = logging.getLogger(__name__)


class Component(object):
    def __init__(self):
        self.config = None
        self.workspace = None

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


class Workload(Component):
    def __init__(self):
        super(Workload, self).__init__()
        self.module = None
        self.parent_module_name = 'scotty.workload_gen'

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'workload_gen.py')


class Experiment(Component):
    def __init__(self):
        super(Experiment, self).__init__()
        self.workloads = {}
        self.resources = {}

    def add_workload(self, workload):
        self.workloads[workload.name] = workload

    def add_resource(self, resource):
        self.resources[resource.name] = resource


class Resource(Component):
    def __init__(self):
        super(Resource, self).__init__()
        self.module = None
        self.parent_module_name = 'scotty.resource_gen'
        self.endpoint = None

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'resource_gen.py')
