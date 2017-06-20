import logging
import os
import sys

from scotty.core.workspace import ResourceWorkspace
from scotty.core.workspace import WorkloadWorkspace
from scotty.core.workspace import ExperimentWorkspace


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
        self.workspace_type = WorkloadWorkspace

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'workload_gen.py')


class Experiment(Component):
    def __init__(self):
        super(Experiment, self).__init__()
        self._workloads = {}
        self._resources = {}
        self.workspace_type = ExperimentWorkspace

    def add_workload(self, workload):
        self._workloads[workload.name] = workload

    def add_resource(self, resource):
        self._resources[resource.name] = resource

    @property
    def workloads(self):
        return self._workloads

    @property
    def resources(self):
        return self._resources


class Resource(Component):
    def __init__(self):
        super(Resource, self).__init__()
        self.module = None
        self.parent_module_name = 'scotty.resource_gen'
        self.workload_type = ResourceWorkspace

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'resource_gen.py')
