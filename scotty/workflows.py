import logging
import yaml

from scotty.config import ScottyConfig
from scotty.core.checkout import CheckoutManager
from scotty.core.moduleloader import ModuleLoader
from scotty.core.workspace import Workspace
from scotty.core.components import Experiment
from scotty.core.components import Workload
from scotty.core.components import Resource
from scotty.core.context import Context
from scotty.core.exceptions import ResourceException
from scotty.core.exceptions import ScottyException

logger = logging.getLogger(__name__)


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self._scotty_config = ScottyConfig()
        self.experiment = None

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
        self.experiment.workspace = Workspace.factory(self.experiment, self._options.workspace)
        self.experiment.workspace.create_paths()

    def _load(self):
        if self._options.config:
            self.experiment.workspace.config_path = self._options.config
        config = self._load_config()
        self.experiment.config = config
        self._load_components(config['resources'], Resource)
        self._load_components(config['workloads'], Workload)

    def _load_components(self, component_configs, component_type):
        for component_config in component_configs:
            logger.info('Load component {}(type: {}, source: {})'.format(
                component_config['name'],
                component_type.__name__,
                component_config['generator']))
            component = component_type()
            component.config = component_config
            workspace_path = self.experiment.workspace.get_component_path(component)
            component.workspace = Workspace.factory(component, workspace_path)
            CheckoutManager.populate(component, self.experiment.workspace.path)
            component.module = ModuleLoader.load_by_component(component)
            self.experiment.add_component(component)

    def _load_config(self):
        config = {}
        with open(self.experiment.workspace.config_path, 'r') as stream:
            config = yaml.load(stream)
        return config

    def _run(self):
        if not self._options.mock:
            self._check_components()
            try:
                self._deploy_resources()
                self._run_workloads()
                self._result_workloads()
            except:
                pass

    def _check_components(self):
        for resource in self.experiment.resources.itervalues():
            logger.info('Check resource ({})'.format(resource.name))
            for interface_ in ('endpoint', 'deploy', 'clean'):
                try:
                    getattr(resource.module, interface_) 
                except:
                    err_msg = 'Missing interface {} for resource {}'.format(
                            interface_, resource.name)
                    logger.error(err_msg)
                    raise ScottyException(err_msg)
        for workload in self.experiment.workloads.itervalues():
            logger.info('Check workload ({})'.format(workload.name))
            for interface_ in ('run', 'result'):
                try:
                    getattr(workload.module, interface_)
                except:
                    err_msg = 'Missing interface ({}) for workload ({})'.format(
                            interface_, resource.name)
                    logger.error(err_msg)
                    raise ScottyException(err_msg)

    def _deploy_resources(self):
        for resource in self.experiment.resources.itervalues():
            logger.info('Deploy resource ({})'.format(resource.name))
            with self.experiment.workspace.cwd():
                context = Context(resource, self.experiment)
                try:
                    resource.module.deploy(context)
                    resource.endpoint = resource.module.endpoint(context)
                except:
                    logger.exception('Error from customer resource ({})'.format(resource.name))
                    raise ResourceException()

    def _run_workloads(self):
        for workload in self.experiment.workloads.itervalues():
            logger.info('Run workload ({})'.format(workload.name))
            with self.experiment.workspace.cwd():
                context = Context(workload, self.experiment)
                try:
                    workload.module.run(context)
                except:
                    logger.exception('Error from customer workload ({})'.format(workload.name))
                    raise WorkloadException()

    def _result_workloads(self):
        pass

    def _clean(self):
        self._clean_resources()

    def _clean_resources(self):
        for resource in self.experiment.resources.itervalues():
             logger.info('Clean resource ({})'.format(resource.name))
             with self.experiment.workspace.cwd():
                context = Context(resource, self.experiment)
                try:
                    resource.module.clean(context)
                except:
                    logger.exception('Error from customer resource ({})'.format(resource.name))
