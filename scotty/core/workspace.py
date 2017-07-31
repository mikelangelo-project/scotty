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
    def factory(cls, component, workspace_path):
        if component.isinstance('Workload'):
            workspace = WorkloadWorkspace(workspace_path)
        elif component.isinstance('Resource'):
            workspace = ResourceWorkspace(workspace_path)
        elif component.isinstance('Experiment'):
            workspace = ExperimentWorkspace(workspace_path)
        else:
            raise ExperimentException('Component {} is not supported'.format(type(component)))
        return workspace


class ExperimentWorkspace(Workspace):
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
        self.scotty_path = os.path.join(self.path, '.scotty')
        self.components_path = os.path.join(
            self.scotty_path,
            'components')
        self.resources_path = os.path.join(
            self.components_path,
            'resources')
        self.workloads_path = os.path.join(
            self.components_path,
            'workloads')
        if not os.path.isdir(self.scotty_path):
            os.mkdir(self.scotty_path)
        if not os.path.isdir(self.components_path):
            os.mkdir(self.components_path)
        if not os.path.isdir(self.workloads_path):
            os.mkdir(self.workloads_path)
        if not os.path.isdir(self.resources_path):
            os.mkdir(self.resources_path)

    def get_component_path(self, component, create_on_demand=False):
        path = None
        if component.isinstance('Workload'):
            path = os.path.join(self.workloads_path, component.name)
        elif component.isinstance('Resource'):
            path = os.path.join(self.resources_path, component.name)
        else:
            raise ExperimentException('Component {} is not supported'.format(type(component)))
        if create_on_demand and not os.path.isdir(path):
            os.mkdir(path)
        return path


class WorkloadWorkspace(Workspace):
    pass


class ResourceWorkspace(Workspace):
    pass
