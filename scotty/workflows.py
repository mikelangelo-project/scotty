import logging
import os
import yaml

import distutils.dir_util as dir_util

from scotty.config import ScottyConfig
from scotty.core.checkout import CheckoutManager
from scotty.core.moduleloader import ModuleLoader
from scotty.core.workspace import ResourceWorkspace
from scotty.core.workspace import WorkloadWorkspace
from scotty.core.workspace import ExperimentWorkspace
from scotty.core.components import Experiment
from scotty.core.components import Workload
from scotty.core.components import Resource
from scotty.core.context import Context
from scotty.core.exceptions import ExperimentException


logger = logging.getLogger(__name__)


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self._checkout_manager = CheckoutManager()
        self._scotty_config = ScottyConfig()

    def run(self):
        self._prepare()
        self._load()
        self._run()
        self._clean()

    def _prepare(self):
        raise NotImplementedError('Workflow._prepare(self) must be implemented')

    def _load(self):
        raise NotImplementedError('Workflow._load(self) must be implemented')

    def _run(self):
        raise NotImplementedError('Workflow._run(self) must be implemented')

    def _clean(self):
        pass


class ExperimentPerformWorkflow(Workflow):
    def _prepare(self):
        self._module_loader = ModuleLoader('scotty.workload_gen', 'anonymous_workload')
        self.experiment = Experiment()
        self.experiment.workspace = ExperimentWorkspace(self._options.workspace)

    def _load(self):
        config = self._load_config()
        self.experiment.config = config
        for workload_config in config['workloads']:
            workload = Workload()
            workload.config = workload_config
            workload.workspace = self._create_workload_workspace(workload)
            self._populate_workload_dir(workload)
            workload.module = self._module_loader.load_by_path(
                workload.module_path, workload.name)
            self.experiment.add_workload(workload)
           
    def _load_config(self):
        config = {}
        with open(self.experiment.workspace.config_path, 'r') as stream:
            config = yaml.load(stream)
        return config
            
    def _populate_workload_dir(self, workload):
        if workload.source_is('git'):
            self._checkout_workload(workload)
        elif workload.source_is('file'):
            self._copy_workload(workload)
        else:
            raise ExperimentException('Unsupported source type. Use "git:" or "file:')
            
    def _checkout_workload(self, workload):
        source = workload.config['generator'].split(':')
        git_url = "{}:{}".format(source[1], source[2])
        git_ref = None
        if len(source) > 3:
            git_ref = source[3]
        logger.info('Clone workload generator ({}) into experiment workload workspace ({})'.format(
            git_url,
            workload.workspace.path))
        self._checkout_manager.checkout(git_url, workload.workspace, git_ref)

    def _copy_workload(self, workload):
        source = workload.config['generator'].split(':')
        logger.info('Copy workload generator ({}) into experiment workload workspace ({})'.format(
            source[1],
            workload.workspace.path))
        if os.path.isabs(source[1]):
            error_message = 'Source ({}) for workload generator ({}) must be relative'.format(
                source[1], 
                workload.name)
            logger.error(error_message)
            raise ExperimentException(error_message)
        source_path = os.path.join(self.experiment.workspace.path, source[1], '.')
        dir_util.copy_tree(source_path, workload.workspace.path)

    def _create_workload_workspace(self, workload):
        workloads_path = self.experiment.workspace.workloads_path
        if not os.path.isdir(workloads_path):
            os.mkdir(workloads_path)
        workspace_path = os.path.join(
            workloads_path,
            workload.config['name'])
        if not os.path.isdir(workspace_path):
            os.mkdir(workspace_path)
        return WorkloadWorkspace(workspace_path)

    def _run(self):
        if not self._options.mock:
            for workload in self.experiment.workloads.itervalues():
                with self.experiment.workspace.cwd():
                    context = Context(workload, self.experiment)
                    try:
                        workload.module.run(context)
                    except:
                        logger.exception(
                            'Error from customer workload generator')


class WorkloadRunWorkflow(Workflow):
    workload = None

    def _prepare(self):
        self._module_loader = ModuleLoader('scotty.workload_gen', 'anonymous_workload')
        if not self.workload:
            self.workload = Workload()
        if not self.workload.workspace:
            self.workload.workspace = WorkloadWorkspace(self._options.workspace)
        if not self.workload.workspace.config_path:
            self.workload.workspace.config_path = self._options.config

    def _load(self):
        self.workload.config = self._load_config()
        self.workload.module = self._module_loader.load_by_path(
                self.workload.module_path, self.workload.name)

    def _load_config(self):
        config = {}
        with open(self.workload.workspace.config_path, 'r') as stream:
            config = yaml.load(stream)
        return config['workload']

    def _run(self):
        if not self._options.mock:
            with self.workload.workspace.cwd():
                context = Context(self.workload)
                try:
                    self.workload.module.run(context)
                except:
                    logger.exception('Error from customer workload generator')


class ResourceDeployWorkflow(Workflow):
    resource = None

    def _prepare(self):
        self._module_loader = ModuleLoader('scotty.component.resource__gen', 'anonymous_resource')
        self.resource = Resource()
        self.resource.workspace = ResourceWorkspace(self._options.workspace)
        self.resource.workspace.config_path = self._options.config

    def _load(self):
        self.resource.config = self._load_config()
        self.resource.module = self._module_loader.load_by_path(
            self.resource.module_path, self.resource.name)

    def _load_config(self):
        config = {}
        with open(self.resource.workspace.config_path, 'r') as stream:
            config = yaml.load(stream)
        return config['resource']

    def _run(self):
        if not self._options.mock:
            context = Context(self.resource)
            try:
                resource.endpoint = self.resource.module.deploy(context)
            except:
                logger.exception('Error from customer resource generator')
