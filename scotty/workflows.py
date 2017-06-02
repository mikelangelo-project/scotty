import logging
import os
import yaml

from scotty.config import ScottyConfig
from scotty.core.checkout import CheckoutManager
from scotty.core.moduleloader import ModuleLoader
from scotty.core.workspace import ResourceWorkspace
from scotty.core.workspace import WorkloadWorkspace 
from scotty.core.workspace import ExperimentWorkspace
from scotty.core.components import Experiment
from scotty.core.components import Workload
from scotty.core.components import Resource
from scotty.core.exceptions import ExperimentException
from scotty.core.exceptions import WorkloadException

logger = logging.getLogger(__name__)


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self._checkout_manager = CheckoutManager()
        self._scotty_config = ScottyConfig()

    def run(self):
        self._prepare()
        self._checkout()
        self._load()
        self._run()
        self._clean()

    def _prepare(self):
        raise NotImplementedError('Workload._prepare(self) must be implemented')

    def _checkout(self):
        raise NotImplementedError('Workload._checkout(self) must be implemented')

    def _load(self):
        raise NotImplementedError('Workload._load(self) must be implemented')

    def _run(self):
        raise NotImplementedError('Workload._run(self) must be implemented')

    def _clean(self):
        pass


class ExperimentPerformWorkflow(Workflow):
    def _prepare(self):
        self._module_loader = ModuleLoader('scotty.workload_gen', 'anonymous_workload')
        self.experiment = Experiment()
        self.experiment.workspace = ExperimentWorkspace(self._options.workspace)

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
            raise ExperimentException(message)
        gerrit_url = self._scotty_config.get('gerrit', 'host') + '/p/'
        self._checkout_manager.checkout(self.experiment.workspace, project,
                                        gerrit_url, zuul_url, zuul_ref)

    def _load(self):
        config = self._load_config()
        self.experiment.config = config
        for workload_config in config['workloads']:
            workload = Workload()
            workload.config = workload_config
            workload.workspace = self._create_workload_workspace(workload)
            self._checkout_workload(workload)
            workload.module = self._module_loader.load_by_path(
                workload.module_path, workload.name)
            self.experiment.add_workload(workload)

    def _load_config(self):
        config = {}
        with open(self.experiment.workspace.config_path, 'r') as stream:
            config = yaml.load(stream)
        return config

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

    def _checkout_workload(self, workload):
        if self._options.skip_checkout:
            return
        git_url = self._scotty_config.get('gerrit', 'host') + '/p/'
        project = 'workload_gen/{}'.format(workload.config['generator'])
        self._checkout_manager.checkout(workload.workspace, project,
                                        git_url, None, 'master')

    def _run(self):
        if not self._options.mock:
            for workload_name, workload in self.experiment.workloads.iteritems(
            ):
                with self.experiment.workspace.cwd():
                    context = workload.context
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
            raise WorkloadException(message)
        git_url = self._scotty_config.get('gerrit', 'host') + '/p/'
        self._checkout_manager.checkout(self.workload.workspace, project,
                                        git_url, zuul_url, zuul_ref)

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
                context = self.workload.context
                try:
                    self.workload.module.run(context)
                except:
                    logger.exception('Error from customer workload generator')


class ResourceDeployWorkflow(Workflow):
    def _prepare(self):
        self._module_loader = ModuleLoader('scotty.component.resource__gen', 'anonymous_resource')
        self.resource = Resource()
        self.resource.workspace = ResourceWorkspace(self._options.workspace)

    def _checkout(self):
        if self._options.skip_checkout:
            return

    def _load(self):
        pass

    def _run(self):
        if not self._options.mock:
            pass
