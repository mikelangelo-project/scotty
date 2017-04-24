import logging
import os
import yaml

import git

import scotty.utils as utils

logger = logging.getLogger(__name__)


class Workspace(object):
    def __init__(self, path, git_=None):
        self.path = path
        if not os.path.isdir(path):
            raise WorkspaceException('{} does not exist or is no directory'.format(path))
        if git_ is None:
            self._git = git.cmd.Git
        else:
            self._git = git_

    @property
    def config_path(self):
        path = os.path.join(self.path, 'experiment.yaml')
        if not os.path.isfile(path):
            path = os.path.join(self.path, 'experiment.yml')
        if not os.path.isfile(path):
            raise WorkspaceException('Could not find the experiment config file.')
        return path 


class Workload(object):
    def __init__(self):
        pass


class WorkloadLoader(object):
    @classmethod
    def load_by_config(cls, config):
        return Workload()


class Experiment(object):
    def add_workload(self, workload):
        pass   

    @property
    def workload(self):
        return self._workload or {}

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def workspace(self):
        return self._workspace

    @workspace.setter
    def workspace(self, value):
        self._workspace = value


class ExperimentConfigLoader(object):
    @classmethod
    def load_by_workspace(cls, workspace):
        with open(workspace.config_path, 'r') as stream:
            dict_ = yaml.load(stream)
        return ExperimentConfig(dict_)

class ExperimentConfig(object):
    def __init__(self, dict_):
        self._dict = dict_

    def __getattr__(self, name):
        return self._dict[name]


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self.experiment = None

    def run(self):
        self._prepare()
        self._checkout()
        self._load()
        self._run()

    def _prepare(self):
        path = os.path.abspath(self._options.workspace)
        self.experiment = self.experiment or Experiment()
        self.experiment.workspace = Workspace(path)

    def _checkout(self):
        if self._options.skip_checkout:
            return
        try:
            project = self._options.project or os.environ['ZUUL_PROJECT']
            zuul_url = self._options.zuul_url or os.environ['ZUUL_URL']
            zuul_ref = self._options.zuul_ref or os.environ['ZUUL_REF']
        except KeyError as e:
            message = 'Missing Zuul settings ({})'.format(e)
            logger.error(message)
            raise CheckoutException(message)
                
    def _load(self):
        workspace = self.experiment.workspace
        config = ExperimentConfigLoader.load_by_workspace(workspace)
        self.experiment.config = config
        for workload_config in config.workloads:
            workload = WorkloadLoader.load_by_config(workload_config)
            self.experiment.add_workload(workload)

    def _run(self):
        pass


class CheckoutException(Exception):
    pass


class WorkspaceException(Exception):
    pass
