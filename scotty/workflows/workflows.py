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
from scotty.core.components import ComponentValidator
from scotty.core.components import ResourceState
from scotty.core.components import WorkloadState
from scotty.core.context import Context
from scotty.core.exceptions import ResourceException
from scotty.core.exceptions import WorkloadException
from scotty.core.exceptions import ScottyException
from scotty.core.report import ReportCollector
from scotty.core.executor import WorkloadRunExecutor
from scotty.core.executor import ResourceDeployExecutor

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
        raise NotImplementedError(
            'Workflow._prepare(self) must be implemented')

    def _load(self):
        pass

    def _run(self):
        raise NotImplementedError('Workflow._run(self) must be implemented')

    def _clean(self):
        pass


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
        self.template_dir = os.path.dirname(os.path.realpath(__file__))
        self.template_dir = os.path.join(self.template_dir, '../../templates')
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
        self._create_readme()

    def _create_workload_gen(self):
        workload_gen_py_template = os.path.join(self.template_dir, 'workload_gen.template.py')
        shutil.copyfile(workload_gen_py_template, self.workload.module_path)

    def _create_samples(self):
        samples_dir = os.path.join(self.workload.workspace.path, 'samples')
        if not os.path.isdir(samples_dir):
            os.mkdir(samples_dir)
        experiment_yaml = os.path.join(samples_dir, 'experiment.yaml')
        experiment_yaml_template = os.path.join(self.template_dir, 'experiment.workload.yaml')
        shutil.copyfile(experiment_yaml_template, experiment_yaml)
         
    def _create_readme(self):
        readme_md = os.path.join(self.workload.workspace.path, 'README.md')
        readme_md_template = os.path.join(self.template_dir, 'README.workload.md')
        shutil.copyfile(readme_md_template, readme_md)


class ResourceInitWorkflow(Workflow):
    def _prepare(self):
        self.template_dir = os.path.dirname(os.path.realpath(__file__))
        self.template_dir = os.path.join(self.template_dir, '../../templates')
        self.resource = Resource()
        self.resource.workspace = Workspace.factory(self.resource, self._options.directory)
        self._check_existing_resource()

    def _check_existing_resource(self):
        if os.path.isfile(self.resource.module_path):
            raise ScottyException(
                'Destination {} is already an existing resource'.format(
                    self.resource.workspace.path))

    def _run(self):
        logger.info(
            'Start to create structure for resource (dir: {})'.format(
                self.resource.workspace.path))
        if not os.path.isdir(self.resource.workspace.path):
            logger.info('Create directory {}'.format(self.resource.workspace.path))
            os.makedirs(self.resource.workspace.path)
        self._create_resource_gen()
        self._create_samples()
        self._create_readme()

    def _create_resource_gen(self):
        resource_gen_py_template = os.path.join(self.template_dir, 'resource_gen.template.py')
        shutil.copyfile(resource_gen_py_template, self.resource.module_path)

    def _create_samples(self):
        samples_dir = os.path.join(self.resource.workspace.path, 'samples')
        if not os.path.isdir(samples_dir):
            os.mkdir(samples_dir)
        experiment_yaml = os.path.join(samples_dir, 'experiment.yaml')
        experiment_yaml_template = os.path.join(self.template_dir, 'experiment.resource.yaml')
        shutil.copyfile(experiment_yaml_template, experiment_yaml)

    def _create_readme(self):
        readme_md = os.path.join(self.resource.workspace.path, 'README.md')
        readme_md_template = os.path.join(self.template_dir, 'README.resource.md')
        shutil.copyfile(readme_md_template, readme_md)
