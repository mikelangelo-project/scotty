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
        cls._initparentmodule('scotty.workload-gen')
        cls._addmodulepath(path)
        module_name = "scotty.workload-gen.{name}".format(name=name)
        workload_ = imp.load_source(module_name, path)
        return workload_

    @classmethod
    def load_by_workspace(cls, workspace, name='ananymous_workload'):
        workload_ = cls.load_by_path(workspace.workload_path, name)
        return workload_

    @classmethod
    def _initparentmodule(cls, parent_mod_name):
        parent_mod = sys.modules.setdefault(parent_mod_name,
                                            imp.new_module(parent_mod_name))
        parent_mod.__file__ = '<virtual %s>' % parent_mod_name

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
        config_path = os.path.join(config_dir, 'workload.yaml')
        if not os.path.isfile(config_path):
            config_path = os.path.join(config_dir, 'workload.yml')
        return config_path

    @property
    def workload_path(self):
        workload_path = os.path.join(self.path, 'workload_gen.py')
        if not os.path.isfile(workload_path):
            workload_path = os.path.join(self.path, 'run.py')
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
            raise Exception('Missing project to checkout')
        git_url = '{g}{p}'.format(g=gerrit_url, p=project)
        g = git.cmd.Git(self.path)
        if not os.path.isdir('{path}/.git'.format(path=self.path)):
            logger.info('    Clone {}'.format(git_url))
            g.clone(git_url, '.')
        g.remote('update')
        g.reset('--hard')
        g.clean('-x', '-f', '-d', '-q')
        if zuul_ref.startswith('refs/tags'):
            raise Exception('Checkout refs/tags not supported')
        else:
            logger.info('    Fetch from zuul merger')
            zuul_git_url = '{z}{p}'.format(z=zuul_url, p=project)
            g.fetch(zuul_git_url, zuul_ref)
            g.checkout('FETCH_HEAD')
            g.reset('--hard', 'FETCH_HEAD')
        g.clean('-x', '-f', '-d', '-q')
        if os.path.isfile('{path}/.gitmodules'.format(path=self.path)):
            logger.info('    Init submodules')
            g.submodules('init')
            g.submodules('sync')
            g.submodules('update', '--init')


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
