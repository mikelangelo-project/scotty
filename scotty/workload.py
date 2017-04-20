import logging
import imp
import contextlib
import os
import sys

import git
import yaml

import scotty.utils as utils

logger = logging.getLogger(__name__)


class WorkloadLoader(object):
    @classmethod
    def load_by_path(cls, path,  name='anonymous_workload'):
        cls._initparentmodule('scotty.workload_gen')
        cls._addmodulepath(path)
        module_name = "scotty.workload_gen.{name}".format(name=name)
        workload_ = imp.load_source(module_name, path)
        return workload_

    @classmethod
    def load_by_workspace(cls, workspace, name='anonymous_workload'):
        workload_ = cls.load_by_path(workspace.workload_path, name)
        return workload_

    @classmethod
    def _initparentmodule(cls, parent_mod_name):
        parent_mod = sys.modules.setdefault(parent_mod_name,
                                            imp.new_module(parent_mod_name))
        parent_mod.__file__ = '<virtual {}>'.format(parent_mod_name)

    @classmethod
    def _addmodulepath(cls, module_path):
        path = os.path.dirname(os.path.abspath(module_path))
        logger.info('path: {}'.format(path))
        sys.path.insert(0, path)


class WorkloadWorkspace(object):
    def __init__(self, path):
        self.path = path

    @property
    def config_path(self):
        config_dir = os.path.join(self.path, 'test')
        if not os.path.isdir(config_dir):
            config_dir = os.path.join(self.path, 'samples')
        if not os.path.isdir(config_dir):
            raise WorkloadException('Could not find a config directory.')
        config_path = os.path.join(config_dir, 'workload.yaml')
        if not os.path.isfile(config_path):
            config_path = os.path.join(config_dir, 'workload.yml')
        if not os.path.isfile(config_path):
            raise WorkloadException('Could not find the config file.')
        return config_path

    @property
    def workload_path(self):
        workload_path = os.path.join(self.path, 'workload_gen.py')
        if not os.path.isfile(workload_path):
            workload_path = os.path.join(self.path, 'run.py')
        if not os.path.isfile(workload_path):
            raise WorkloadException('Could not find the workload module')
        return workload_path

    @contextlib.contextmanager
    def cwd(self):
        prev_cwd = os.getcwd()
        os.chdir(self.path)
        yield
        os.chdir(prev_cwd)

    def checkout(self, project, gerrit_url, zuul_url, zuul_ref):
        logger.info('Checkout workspace')
        logger.info('    project: {}'.format(project))
        logger.info('    workspace: {}'.format(self.path))
        logger.info('    gerrit_url: {}'.format(gerrit_url))
        logger.info('    zuul_url: {}'.format(zuul_url))
        logger.info('    zuul_ref: {}'.format(zuul_ref))
        if not project:
            raise WorkloadException('Missing project to checkout')
        git_url = '{git_repo}{project}'.format(git_repo=gerrit_url, project=project)
        git_repo = self._prepare_repo(git_url)
        self._clean_repo(git_repo)
        self._update_repo_from_zuul(git_repo, zuul_ref, zuul_url, project)
        git_repo.clean('-x', '-f', '-d', '-q')
        self._init_submodules(git_repo)

    def _prepare_repo(self, git_url):
        git_repo = git.cmd.Git(self.path)
        if not os.path.isdir('{path}/.git'.format(path=self.path)):
            logger.info('    Clone {}'.format(git_url))
            git_repo.clone(git_url, '.')
        return git_repo

    def _clean_repo(self, git_repo):
        git_repo.remote('update')
        git_repo.reset('--hard')
        git_repo.clean('-x', '-f', '-d', '-q')

    def _update_repo_from_zuul(self, git_repo, zuul_ref, zuul_url, project):
        if zuul_ref.startswith('refs/tags'):
            raise WorkloadException('Checkout of refs/tags not supported')
        else:
            logger.info('    Fetch from zuul merger')
            zuul_git_url = '{z}{p}'.format(z=zuul_url, p=project)
            git_repo.fetch(zuul_git_url, zuul_ref)
            git_repo.checkout('FETCH_HEAD')
            git_repo.reset('--hard', 'FETCH_HEAD')

    def _init_submodules(self, git_repo):
        if os.path.isfile('{path}/.gitmodules'.format(path=self.path)):
            logger.info('    Init submodules')
            git_repo.submodules('init')
            git_repo.submodules('sync')
            git_repo.submodules('update', '--init')


class WorkloadConfigLoader(object):
    @classmethod
    def load_by_workspace(cls, workspace):
        with open(workspace.config_path, 'r') as stream:
            dict_ = yaml.load(stream)
        return WorkloadConfig(dict_['workload'])


class WorkloadConfig(object):
    def __init__(self, dict_):
        self._dict = dict_

    def __getattr__(self, name):
        return self._dict[name]


class BaseContext(object):
    def __getattr__(self, name):
        return self._context[name]


class Context(BaseContext):
    def __init__(self, workload_config):
        self._context = {}
        self._context['v1'] = ContextV1(workload_config)


class ContextV1(BaseContext):
    def __init__(self, workload_config):
        self._context = {}
        self._context['workload_config'] = workload_config


class Workflow(object):
    def __init__(self, options):
        self._options = options

    def run(self):
        self._prepare()
        self._checkout()
        self._load()
        self._run()

    def _prepare(self):
        path = os.path.abspath(self._options.workspace)
        self._workspace = WorkloadWorkspace(path)

    def _checkout(self):
        if self._options.skip_checkout:
            return
        try:
            if self._options.project:
                project = self._options.project
            else:
                project = os.environ['ZUUL_PROJECT']
            zuul_url = os.environ['ZUUL_URL']
            zuul_ref = os.environ['ZUUL_REF']
        except KeyError as e:
            logger.error('Missing environment key ({})'.format(e))
            sys.exit(1)
        gerrit_url = utils.Config().get('gerrit', 'host') + '/p/'
        self._workspace.checkout(project, gerrit_url, zuul_url, zuul_ref)

    def _load(self):
        self._config = WorkloadConfigLoader.load_by_workspace(self._workspace)
        self._context = Context(self._config)

    def _run(self):
        workload_ = WorkloadLoader.load_by_workspace(self._workspace,
                                                     self._config.name)
        if not self._options.mock:
            with self._workspace.cwd():
                try:
                    workload_.run(self._context)
                except:
                    logger.exception('Error from customer workload generator')


class WorkloadException(Exception):
    pass
