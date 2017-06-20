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
        self.experiment = Experiment()
        self.experiment.workspace = ExperimentWorkspace(self._options.workspace)
        self.experiment.workspace.create_paths()

    def _load(self):
        config = self._load_config()
        self.experiment.config = config
        for resource_config in config['resources']:
            resource = Resource()
            resource.config = resource_config
            self._load_component(resource)
            self.experiment.add_resource(resource)
        for workload_config in config['workloads']:
            workload = Workload()
            workload.config = workload_config
            self._load_component(workload)
            self.experiment.add_workload(workload)

    def _load_config(self):
        config = {}
        with open(self.experiment.workspace.config_path, 'r') as stream:
            config = yaml.load(stream)
        return config

    def _load_component(self, component):
        component.workspace = self._create_component_workspace(component)
        self._populate_component(component)
        component.module = ModuleLoader.load_by_component(component)

    def _populate_component(self, component):
        if component.issource('git'):
            self._checkout_component(component)
        elif component.issource('file'):
            self._copy_component(component)
        else:
            raise ExperimentException('Unsupported source type, Use "git" or "file"')

    def _checkout_component(self, component):
        source = component.config['generator'].split(':')
        git_url = "{}:{}".format(source[1], source[2])
        git_ref = None
        if len(source) > 3:
            git_ref = source[3]
        logger.info('Clone component generator ({}) into workspace ({})'.format(
            git_url,
            component.workspace.path))
        self._checkout_manager.checkout(git_url, component.workspace, git_ref)

    def _copy_component(self, component):
        source = component.config['generator'].split(':')
        source_path = source[1]
        logger.info('Copy component generator ({}) into workspace ({})'.format(
            source_path,
            component.workspace.path))
        if os.path.isabs(source[1]):
            error_message = 'Source ({}) for component generator ({}) must be relative'.format(
                source_path,
                component.name)
            logger.error(error_message)
            raise ExperimentException(error_message)
        source_path_abs = os.path.join(self.experiment.workspace.path, source_path, '.')
        dir_util.copy_tree(source_path_abs, component.workspace.path)

    def _create_component_workspace(self, component):
        workspace_path = self.experiment.workspace.get_component_path(component)
        if component.isinstance('Workload'):
            workspace = WorkloadWorkspace(workspace_path)
        elif component.isinstance('Resource'):
            workspace = ResourceWorkspace(workspace_path)
        else:
            raise ExperimentException('Component {} is not supported'.format(type(component)))
        if not os.path.isdir(workspace.path):
            os.mkdir(workspace.path)
        return workspace

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
        if not self.workload:
            self.workload = Workload()
        if not self.workload.workspace:
            self.workload.workspace = WorkloadWorkspace(self._options.workspace)
        if not self.workload.workspace.config_path:
            self.workload.workspace.config_path = self._options.config

    def _load(self):
        self.workload.config = self._load_config()
        self.workload.module = ModuleLoader.load_by_component(self.workload) 

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
        self.resource = Resource()
        self.resource.workspace = ResourceWorkspace(self._options.workspace)
        self.resource.workspace.config_path = self._options.config

    def _load(self):
        self.resource.config = self._load_config()
        self.resource.module = ModuleLoader.load_by_component(self.resource)

    def _load_config(self):
        config = {}
        with open(self.resource.workspace.config_path, 'r') as stream:
            config = yaml.load(stream)
        return config['resource']

    def _run(self):
        if not self._options.mock:
            context = Context(self.resource)
            try:
                self.resource.endpoint = self.resource.module.deploy(context)
            except:
                logger.exception('Error from customer resource generator')
