import logging
import yaml
import os

import shutil

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
        pass

    def _load(self):
        pass

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
        if 'resources' in config:
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


class ExperimentCleanWorkflow(Workflow):
    def _prepare(self):
        self.experiment = Experiment()
        self.experiment.workspace = Workspace.factory(self.experiment, self._options.workspace)
        self.experiment.workspace.create_paths()

    def _run(self):
        logger.info('Delete scotty path ({})'.format(self.experiment.workspace.scotty_path))
        shutil.rmtree(self.experiment.workspace.scotty_path)

class WorkloadInitWorkflow(Workflow):
    def _prepare(self):
        self.workload = Workload()
        self.workload.workspace = Workspace.factory(self.workload, self._options.directory)
        self._check_existing_workload()

    def _check_existing_workload(self):
        if os.path.isfile(self.workload.module_path):
            raise ScottyException(
                'Destination {} is already an existing workload'.format(
                    self.workload.workspace.path))

    def _run(self):
        logger.info(
            'Start to create structure for workload (dir: {})'.format(
                self.workload.workspace.path))
        if not os.path.isdir(self.workload.workspace.path):
            logger.info('Create directory {}'.format(self.workload.workspace.path))
            os.makedirs(self.workload.workspace.path)
        self._create_workload_gen()
        self._create_samples()

    def _create_workload_gen(self):
        with open(self.workload.module_path, 'w+') as wm_file:
            wm_file.write('import logging\n')
            wm_file.write('\n')
            wm_file.write('from scotty import utils\n')
            wm_file.write('\n')
            wm_file.write('logger = logging.getLogger(__name__)')
            wm_file.write('\n')
            wm_file.write('\n')
            wm_file.write('def result(context):\n')
            wm_file.write('    pass\n')
            wm_file.write('\n')
            wm_file.write('def run(context):\n')
            wm_file.write('    workload = context.v1.workload\n')
            wm_file.write('    exp_helper = utils.ExperimentHelper(context)\n')
            wm_file.write('#    my_resource = exp_helper.get_resource(workload.resources[\'my_resource\']\n')
            wm_file.write('    print \'{}\'.format(workload.params[\'greeting\'])\n')
            wm_file.write('    print \'I\\\'m workload generator {}\'.format(workload.name)\n')
            wm_file.write('#    print \'The resource endpoint is {}\'.format(my_resource)\n')

    def _create_samples(self):
        samples_dir = os.path.join(self.workload.workspace.path, 'samples')
        if not os.path.isdir(samples_dir):
            os.mkdir(samples_dir)
        sample_exp_yaml = os.path.join(samples_dir, 'experiment.yaml')
        with open(sample_exp_yaml, 'w+') as exp_file:
            exp_file.write('description: my experiment with my workload\n')
            exp_file.write('tags:\n')
            exp_file.write('  - my_tag\n')
            exp_file.write('#resources:\n')
            exp_file.write('#  - name: my_resource_def\n')
            exp_file.write('#    generator: git:git@gitlab.gwdg.de:scotty/resource/demo.git\n')
            exp_file.write('#    params:\n')
            exp_file.write('#      user: myuser\n')
            exp_file.write('#      passwd: <%= ENV[\'mysecret\'] %>\n')
            exp_file.write('workloads:\n')
            exp_file.write('  - name: myworkload\n')
            exp_file.write('    generator: file:.\n')
            exp_file.write('    params:\n')
            exp_file.write('      greeting: Hallo\n')
            exp_file.write('#    resource:\n')
            exp_file.write('#      my_resource: my_resource_def\n')
