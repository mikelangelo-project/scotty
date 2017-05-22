import logging
import os
import yaml
import contextlib

from scotty.config import ScottyConfig
import scotty.core.workload
import scotty.core.exceptions
import scotty.core.checkout

logger = logging.getLogger(__name__)


class Workspace(object):
    def __init__(self, path):
        self.path = path
        if not os.path.isdir(path):
            raise scotty.core.exceptions.ExperimentException(
                '{} does not exist or is no directory'.format(path))

    @property
    def config_path(self):
        path = os.path.join(self.path, 'experiment.yaml')
        if not os.path.isfile(path):
            path = os.path.join(self.path, 'experiment.yml')
        if not os.path.isfile(path):
            raise scotty.core.exceptions.ExperimentException(
                'Could not find the experiment config file.')
        return path

    @property
    def workloads_path(self):
        path = os.path.join(self.path, '.workloads/')
        return path

    @contextlib.contextmanager
    def cwd(self):
        prev_cwd = os.getcwd()
        os.chdir(self.path)
        yield
        os.chdir(prev_cwd)


class ExperimentLoader(object):
    @classmethod
    def load_from_workspace(cls, workspace, experiment_config):
        experiment = Experiment()
        experiment.workspace = workspace
        experiment.config = experiment_config
        cls._create_workloads_dir(workspace)
        return experiment

    @classmethod
    def _create_workloads_dir(cls, workspace):
        if not os.path.isdir(workspace.workloads_path):
            os.mkdir(workspace.workloads_path)


class Experiment(object):
    def __init__(self):
        self._workloads = {}
        self.config = None
        self.workspace = None

    def add_workload(self, workload):
        self._workloads[workload.name] = workload

    @property
    def workloads(self):
        return self._workloads


class ExperimentConfigLoader(object):
    @classmethod
    def load_by_workspace(cls, workspace):
        with open(workspace.config_path, 'r') as stream:
            dict_ = yaml.load(stream)
        return dict_


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self._scotty_config = ScottyConfig()
        self._checkout_manager = scotty.core.checkout.Manager()
        self.workspace = None

    def perform(self):
        self._prepare()
        self._checkout()
        self._load()
        self._perform()

    def _prepare(self):
        path = os.path.abspath(self._options.workspace)
        self.workspace = self.workspace or Workspace(path)

    def _checkout(self):
        if self._options.skip_checkout:
            return
        try:
            project = self._options.project or os.environ['ZUUL_PROJECT']
            zuul_url = os.environ['ZUUL_URL']
            zuul_ref = os.environ['ZUUL_REF']
        except KeyError as e:
            message = 'Missing Zuul settings ({})'.format(e)
            logger.error(message)
            raise scotty.core.exceptions.ExperimentException(message)
        gerrit_url = self._scotty_config.get('gerrit', 'host') + '/p/'
        self._checkout_manager.checkout(self.workspace, project, gerrit_url,
                                        zuul_url, zuul_ref)

    def _load(self):
        config = ExperimentConfigLoader.load_by_workspace(self.workspace)
        self.experiment = ExperimentLoader().load_from_workspace(
            self.workspace, config)
        for workload_config in config['workloads']:
            workload_path = os.path.join(
                self.experiment.workspace.workloads_path,
                workload_config['name'])
            workload = self._load_workload(workload_path, workload_config)
            self.experiment.add_workload(workload)

    def _load_workload(self, path, workload_config):
        if not os.path.isdir(path):
            os.mkdir(path)
        workspace = scotty.core.workload.Workspace(path)
        if not self._options.skip_checkout:
            gerrit_url = self._scotty_config.get('gerrit', 'host') + '/p/'
            project = 'workload_gen/{}'.format(workload_config['generator'])
            scotty.core.checkout.Manager().checkout(workspace, project,
                                                    gerrit_url, None, 'master')
        workload = scotty.core.workload.WorkloadLoader().load_from_workspace(
            workspace, workload_config)
        return workload

    def _perform(self):
        if not self._options.mock:
            for workload_name, workload in self.experiment.workloads.iteritems(
            ):
                with self.experiment.workspace.cwd():
                    try:
                        context = workload.context
                        workload.module.run(context)
                    except:
                        logger.exception(
                            'Error from customer workload generator')
