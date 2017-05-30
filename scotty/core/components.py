import logging
import os

from scotty.core.context import Context

logger = logging.getLogger(__name__)


class Component(object):
    def __init__(self):
        self.config = None
        self.workspace = None

    @property
    def name(self):
        return self.config['name']


class Workload(Component):
    def __init__(self):
        super(Workload, self).__init__()
        self.module = None

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'workload_gen.py')

    @property
    def context(self):
        return Context(self.config)


class Experiment(Component):
    def __init__(self):
        super(Experiment, self).__init__()
        self._workloads = {}
        self._resources = {}

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
