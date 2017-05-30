import logging
import imp
import contextlib
import os
import sys

import yaml

from scotty.config import ScottyConfig
from scotty.core.checkout import CheckoutManager
from scotty.core import exceptions
from scotty.core.moduleloader import ModuleLoader 
from scotty.core.workspace import Workspace

logger = logging.getLogger(__name__)


class Workload(object):
    def __init__(self):
        self.module = None
        self.config = None
        self.workspace = None

    @property
    def name(self):
        return self.config['name']

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'workload_gen.py')

    @property
    def context(self):
        return Context(self.config)


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
        self._module_loader = ModuleLoader('scotty.workload_gen', 'anonymous_workload')
        self.workload = None
        self._scotty_config = ScottyConfig()

    def run(self):
        self._prepare()
        self._checkout()
        self._load()
        self._run()

    def _prepare(self):
        if not self.workload:
            self.workload = Workload()
        if not self.workload.workspace:
            self.workload.workspace = Workspace(self._options.workspace)

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
        self._checkout_manager.checkout(self.workload.workspace,
                                        project,
                                        gerrit_url,
                                        zuul_url,
                                        zuul_ref)

    def _load(self):
        config = WorkloadConfigLoader.load_by_path(self._options.config)
        module_path = self.workload.module_path
        self.workload.config = config
        self.workload.module = self._module_loader.load_by_path(module_path, config['name']) 

    def _run(self):
        if not self._options.mock:
            with self.workload.workspace.cwd():
                try:
                    context = self.workload.context
                    self.workload.module.run(context)
                except:
                    logger.exception('Error from customer workload generator')
