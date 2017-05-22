import logging
import imp
import contextlib
import os
import sys

import yaml

from scotty.config import ScottyConfig
import scotty.core.experiment
from scotty.core.checkout import CheckoutManager
from scotty.core import exceptions

logger = logging.getLogger(__name__)


class WorkloadModuleLoader(object):
    @classmethod
    def load_by_path(cls, path, name='anonymous_workload'):
        cls._initparentmodule('scotty.workload_gen')
        cls._addmodulepath(path)
        module_name = "scotty.workload_gen.{name}".format(name=name)
        workload_ = imp.load_source(module_name, path)
        return workload_

    @classmethod
    def load_by_workspace(cls, workspace, name='anonymous_workload'):
        workload_ = cls.load_by_path(workspace.module_path, name)
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


class Workload(object):
    def __init__(self):
        self.module = None
        self.config = None
        self.workspace = None

    @property
    def name(self):
        return self.config['name']

    @property
    def context(self):
        return Context(self.config)


class WorkloadLoader(object):
    @classmethod
    def load_from_workspace(cls, workspace, config):
        module_ = WorkloadModuleLoader.load_by_workspace(workspace, config['name'])
        workload = Workload()
        workload.workspace = workspace
        workload.module = module_
        workload.config = config
        return workload


class Workspace(object):
    def __init__(self, path):
        self.path = path

    @property
    def module_path(self):
        module_path = os.path.join(self.path, 'workload_gen.py')
        if not os.path.isfile(module_path):
            module_path = os.path.join(self.path, 'run.py')
        if not os.path.isfile(module_path):
            raise exceptions.WorkloadException('Could not find the workload module')
        return module_path

    @contextlib.contextmanager
    def cwd(self):
        prev_cwd = os.getcwd()
        os.chdir(self.path)
        yield
        os.chdir(prev_cwd)


class WorkloadConfigLoader(object):
    @classmethod
    def load_by_path(cls, path):
        try:
            with open(path, 'r') as stream:
                dict_ = yaml.load(stream)
            return dict_['workload']
        except IOError as e:
            logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))
            logger.error("Failed to load workload config: {0}".format(path))
            sys.exit(1)


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
        self._checkout_manager = CheckoutManager()
        self.workspace = None
        self._scotty_config = ScottyConfig()

    def run(self):
        self._prepare()
        self._checkout()
        self._load()
        self._run()

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
            message = 'Missing zuul setting ({})'.format(e)
            logger.error(message)
            raise exceptions.WorkloadException(message)
        gerrit_url = self._scotty_config.get('gerrit', 'host') + '/p/'
        self._checkout_manager.checkout(self.workspace,
                                        project,
                                        gerrit_url,
                                        zuul_url,
                                        zuul_ref)

    def _load(self):
        config = WorkloadConfigLoader.load_by_path(self._options.config)
        self.workload = WorkloadLoader().load_from_workspace(self.workspace, config)

    def _run(self):
        if not self._options.mock:
            with self.workspace.cwd():
                try:
                    context = self.workload.context
                    self.workload.module.run(context)
                except:
                    logger.exception('Error from customer workload generator')
