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


class ExperimentWorkspace(Workspace):
    @property
    def config_path(self):
        path = os.path.join(self.path, 'experiment.yaml')
        if not os.path.isfile(path):
            path = os.path.join(self.path, 'experiment.yml')
        if not os.path.isfile(path):
            raise ExperimentException('Could not find the experiment config file.')
        return path

    @property
    def workloads_path(self):
        path = os.path.join(self.path, '.workloads')
        return path


class WorkloadWorkspace(Workspace):
    pass


class ResourceWorkspace(Workspace):
    pass
