import logging
import imp
import contextlib
import os
import sys

import yaml

logger = logging.getLogger(__name__)


class WorkloadLoader(object):
    @classmethod
    def load_by_path(cls, path,  name='anonymous_workload'):
        cls._initparentmodule('scotty.workload-gen')
        module_name = "scotty.workload-gen.{name}".format(name=name)
        workload_ = imp.load_source(module_name, path)
        return workload_

    @classmethod
    def load_by_workspace(cls, workspace, name='ananymous_workload'):
        cls._initparentmodule('scotty.workload-gen')
        module_name = 'scotty.workload-gen.{name}'.format(name=name)
        workload_ = imp.load_source(module_name, workspace.workload_path)
        return workload_

    @classmethod
    def _initparentmodule(cls, parent_mod_name):
        parent_mod = sys.modules.setdefault(parent_mod_name,
                                            imp.new_module(parent_mod_name))
        parent_mod.__file__ = '<virtual %s>' % parent_mod_name


class WorkloadWorkspace(object):
    def __init__(self, path):
        self.path = path

    @property
    def config_path(self):
        return self.path + '/workload.yaml'

    @property
    def workload_path(self):
        return self.path + '/workload_gen.py'

    @contextlib.contextmanager
    def cwd(self):
        prev_cwd = os.getcwd()
        os.chdir(self.path)
        yield
        os.chdir(prev_cwd)

    def checkout(self, project):
        pass


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
        self._workspace = WorkloadWorkspace(self._options.workspace)

    def _checkout(self):
        if self._options.skip_checkout:
            return
        self._workspace.checkout(self._options.project)

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
