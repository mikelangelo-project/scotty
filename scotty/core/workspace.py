import os
import contextlib

from scotty.core.exceptions import ExperimentException

class Workspace(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self._config_path = None

    @property
    def config_path(self):
        return self._config_path

    @config_path.setter
    def config_path(self, path):
        self._config_path = path

    @contextlib.contextmanager
    def cwd(self):
        prev_cwd = os.getcwd()
        os.chdir(self.path)
        yield
        os.chdir(prev_cwd)

    @classmethod
    def factory(cls, component, workspace_path, create_paths = False):
        if component.isinstance('Workload'):
            workspace = WorkloadWorkspace(workspace_path)
        elif component.isinstance('Resource'):
            workspace = ResourceWorkspace(workspace_path)
        elif component.isinstance('SystemCollector'):
            workspace = SystemCollectorWorkspace(workspace_path)
        elif component.isinstance('Experiment'):
            workspace = ExperimentWorkspace(workspace_path)
        elif component.isinstance('ResultStore'):
            workspace = ResultStoreWorkspace(workspace_path)
        else:
            raise ExperimentException('Component {} is not supported'.format(type(component)))
        if create_paths:
            workspace.create_paths()
        return workspace


class ExperimentWorkspace(Workspace):
    supported_components = [
        'resource',
        'systemcollector',
        'workload',
        'resultstore'
    ]
    
    @property
    def config_path(self):
        if not self._config_path:
            path = os.path.join(self.path, 'experiment.yaml')
            if not os.path.isfile(path):
                path = os.path.join(self.path, 'experiment.yml')
            self._config_path = path
        if not os.path.isfile(self._config_path):
            raise ExperimentException('Could not find the experiment config file.')
        return self._config_path

    @config_path.setter
    def config_path(self, path):
        self._config_path = path

    def create_paths(self):
        self.create_base_paths()
        self.component_path = {}
        map(self.create_component_path, self.supported_components) 

    def create_base_paths(self):
        self.scotty_path = os.path.join(self.path, '.scotty')
        self.components_base_path = os.path.join(self.scotty_path, 'components')
        self.create_path(self.scotty_path)
        self.create_path(self.components_base_path)

    def create_component_path(self, component_type):
        path = os.path.join(self.components_base_path, component_type)
        self.create_path(path)
        self.component_path[component_type] = path

    def create_path(self, path):
        if not os.path.isdir(path):
            os.mkdir(path)

    def get_component_path(self, component, create_on_demand=False):
        if component.type in self.supported_components:
            path = os.path.join(self.component_path[component.type], component.name)
            if create_on_demand:
                self.create_path(path)
            return path
        else:
            msg = 'Component {} is not supported'
            raise ExperimentException(msg.format(type(component)))


class WorkloadWorkspace(Workspace):
    pass


class ResourceWorkspace(Workspace):
    pass


class SystemCollectorWorkspace(Workspace):
    pass


class ResultStoreWorkspace(Workspace):
    pass
