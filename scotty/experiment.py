import logging
import os
import yaml
import contextlib

import git

import scotty.utils as utils
import scotty.workload

logger = logging.getLogger(__name__)


class CheckoutManager(object):
    def checkout(self, workspace, project, origin_url, update_url, ref):
        url = '{url}{project}'.format(url=origin_url, project=project)
        repo = self._create_repo(workspace, url)
        self._clean_repo(repo, True)
        if not update_url:
            update_url = origin_url
        url = '{url}{project}'.format(url=update_url, project=project)
        self._update_repo(repo, url, ref)
        self._clean_repo(repo)
        self._init_submodules(workspace, repo)

    def _create_repo(self, workspace, url):
        repo = git.cmd.Git(workspace.path)
        if not os.path.isdir('{path}/.git'.format(path=workspace.path)):
            repo.clone(url, '.')
        return repo

    def _clean_repo(self, repo, reset=False):
        if reset:
            repo.remote('update')
            repo.reset('--hard')
        repo.clean('-x', '-f', '-d', '-q')

    def _update_repo(self, repo, url, ref):
        if ref.startswith('refs/tags'):
            raise CheckoutException('Checkout of refs/tags not supported')
        else:
            repo.fetch(url, ref)
            repo.checkout('FETCH_HEAD')
            repo.reset('--hard', 'FETCH_HEAD')

    def _init_submodules(self, workspace, repo):
        if os.path.isfile('{path}/.gitmodules'.format(path=workspace.path)):
            repo.submodules('init')
            repo.submodules('sync')
            repo.submodules('update', '--init')


class Workspace(object):
    def __init__(self, path):
        self.path = path
        if not os.path.isdir(path):
            raise WorkspaceException(
                '{} does not exist or is no directory'.format(path))

    @property
    def config_path(self):
        path = os.path.join(self.path, 'experiment.yaml')
        if not os.path.isfile(path):
            path = os.path.join(self.path, 'experiment.yml')
        if not os.path.isfile(path):
            raise WorkspaceException(
                'Could not find the experiment config file.')
        return path

    @contextlib.contextmanager
    def cwd(self):
        prev_cwd = os.getcwd()
        os.chdir(self.path)
        yield
        os.chdir(prev_cwd)


class Workload(object):
    def __init__(self):
        pass

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, value):
        self._module = value

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

    @property
    def name(self):
        return self._config['name']

    @property
    def context(self):
        return scotty.workload.Context(self._config)


class WorkloadLoader(object):
    @classmethod
    def load_from_workspace(cls, workspace):
        module_ = scotty.workload.WorkloadLoader.load_by_workspace(workspace)
        workload = Workload()
        workload.workspace = workspace
        workload.module = module_
        return workload


class Experiment(object):
    def __init__(self):
        self._workloads = {}

    def add_workload(self, workload):
        self._workloads[workload.name] = workload
        pass

    @property
    def workloads(self):
        return self._workloads

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
        return dict_


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self._config = utils.Config()
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
            zuul_url = os.environ['ZUUL_URL']
            zuul_ref = os.environ['ZUUL_REF']
        except KeyError as e:
            message = 'Missing Zuul settings ({})'.format(e)
            logger.error(message)
            raise CheckoutException(message)
        gerrit_url = self._config.get('gerrit', 'host') + '/p/'
        workspace = self.experiment.workspace
        CheckoutManager().checkout(workspace, project, gerrit_url, zuul_url,
                                   zuul_ref)

    def _load(self):
        workspace = self.experiment.workspace
        workloads_path = os.path.join(workspace.path, '.workloads')
        if not os.path.isdir(workloads_path):
            os.mkdir(workloads_path)
        exp_config = ExperimentConfigLoader.load_by_workspace(workspace)
        self.experiment.config = exp_config
        for workload_dict in exp_config['workloads']:
            workload = self._load_workload(workloads_path, workload_dict)
            self.experiment.add_workload(workload)

    def _load_workload(self, root_path, workload_dict):
        workload_config = workload_dict
        path = os.path.join(root_path, workload_config['name'])
        if not os.path.isdir(path):
            os.mkdir(path)
        workspace = scotty.workload.WorkloadWorkspace(path)
        gerrit_url = self._config.get('gerrit', 'host') + '/p/'
        if not self._options.skip_checkout:
            # TODO split generator by : into generator and reference
            generator = workload_config['generator']
            project = 'workload_gen/{}'.format(generator)
            CheckoutManager().checkout(workspace, project, gerrit_url, None, 'master')
        workload = WorkloadLoader.load_from_workspace(workspace)
        workload.config = workload_config
        return workload

    def _run(self):
        if not self._options.mock:
            for workload_name, workload in self.experiment.workloads.iteritems():
                with self.experiment.workspace.cwd():
                    try:
                        context = workload.context
                        workload.module.run(context)
                    except:
                        logger.exception(
                            'Error from customer workload generator')


class CheckoutException(Exception):
    pass


class WorkspaceException(Exception):
    pass
