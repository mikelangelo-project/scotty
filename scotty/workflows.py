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


class ExperimentPerformWorkflow(Workflow):
    def _prepare(self):
        self._prepare_experiment()
        self._prepare_resources()
        self._prepare_workloads()

    def _prepare_experiment(self):
        logger.info('Prepare experiment')
        experiment = Experiment()
        experiment.workspace = Workspace.factory(experiment,
                                                 self._options.workspace,
                                                 True)
        if self._options.config:
            experiment.workspace.config_path = self._options.config
        with open(experiment.workspace.config_path, 'r') as stream:
            experiment.config = yaml.load(stream)
        self.report_collector = ReportCollector(experiment)
        resource_count = len(experiment.config.get('resources', []))
        workload_count = len(experiment.config.get('workloads', []))
        logger.info('Found {} resource(s) and {} workload(s)'.format(resource_count, workload_count))
        self.experiment = experiment

    def _prepare_resources(self):
        logger.info('Prepare resources')
        resource_configs = self.experiment.config.get('resources', [])
        for resource_config in resource_configs:
            logger.info('Prepare resource {} ({})'.format(resource_config['name'], 
                                                          resource_config['generator']))
            resource = Resource()
            resource.config = resource_config
            resource_path = self.experiment.workspace.get_component_path(resource)
            resource.workspace = Workspace.factory(resource, resource_path)
            CheckoutManager.populate(resource, self.experiment.workspace.path)
            resource.module = ModuleLoader.load_by_component(resource)
            ComponentValidator.validate_interfaces(resource)
            self.experiment.add_component(resource)

    def _prepare_workloads(self):
        logger.info('Prepare workloads')
        workload_configs = self.experiment.config.get('workloads', [])
        for workload_config in workload_configs:
            logger.info('Prepare workload {} ({})'.format(workload_config['name'],
                                                          workload_config['generator']))
            workload = Workload()
            workload.config = workload_config
            workload_path = self.experiment.workspace.get_component_path(workload)
            workload.workspace = Workspace.factory(workload, workload_path)
            CheckoutManager.populate(workload, self.experiment.workspace.path)
            workload.module = ModuleLoader.load_by_component(workload)
            ComponentValidator.validate_interfaces(workload)
            self.experiment.add_component(workload)

    def _run(self):
        self._run_resources_deploy()
        self._run_resources_endpoint()
        self._run_report_static()
        self._run_workloads()
        self._run_workloads_report()
        self._run_report()

    def _run_resources_deploy(self):
        logger.info('Deploy resources')
        for resource in self.experiment.resources.itervalues():
            logger.info('Deploy resource {}'.format(resource.name))
            with self.experiment.workspace.cwd():
                context = Context(resource, self.experiment)
                try:
                    resource.state = ResourceState.DEPLOYING
                    resource.module.deploy(context)
                except:
                    resource.state = ResourceState.ERROR
                    logger.exception('Error from customer resource ({})'.format(resource.name))
                    raise ResourceException()

    def _run_resources_endpoint(self):
        logger.info('Wait for resource endpoints')
        while True:
            retry = False
            for resource in self.experiment.resources.itervalues():
                if resource.state is ResourceState.DEPLOYING:
                    with self.experiment.workspace.cwd():
                        context = Context(resource, self.experiment)
                        try:
                            resource.endpoint = resource.module.endpoint(context)
                            if resource.endpoint is not None:
                                resource.state = ResourceState.ACTIVE
                            else:
                                retry = True
                        except:
                            resource.state = ResourceState.ERROR
            if not retry:
                break

    def _run_report_static(self):
        logger.info('Collect static metrics')
        self.report_collector.collect_static()

    def _run_workloads(self):
        logger.info('Run workloads')
        for workload in self.experiment.workloads.itervalues():
            logger.info('Run workload {}'.format(workload.name))
            with self.experiment.workspace.cwd():
                context = Context(workload, self.experiment)
                try:
                    workload.state = WorkloadState.ACTIVE
                    workload.module.run(context)
                except:
                    workload.state = WorkloadState.ERROR
                    logger.exception('Error from customer workload ({})'.format(workload.name))
                    raise WorkloadException()

    def _run_workloads_report(self):
        logger.info('Wait for workload results')
        while True:
            retry = False
            for workload in self.experiment.workloads.itervalues():
                if workload.state is WorkloadState.ACTIVE:
                     with self.experiment.workspace.cwd():
                         context = Context(workload, self.experiment)
                         try:
                             workload.result = workload.module.result(context)
                             if workload.result is True:
                                 workload.state = WorkloadState.FINISHED
                             else:
                                 retry = True
                         except:
                             workload.state = WorkloadState.ERROR
            if not retry:
                break;

    def _run_report(self):
        logger.info('Collect result and metrics')
        self.report_collector.collect()

    def _clean(self):
        self._clean_workloads()
        self._clean_resources()
        self._clean_experiment()

    def _clean_workloads(self):
        logger.info('Clean workloads')
        for workload in self.experiment.workloads.itervalues():
            logger.info('Clean workload {}'.format(workload.name))
            with self.experiment.workspace.cwd():
                context = Context(workload, self.experiment)
                has_clean = False
                try:
                    getattr(workload.module, 'clean')
                    has_clean = True
                except:
                    logger.warning('Missing interface clean for {} workload'.format(
                        workload.name))
                if has_clean:
                    try:
                        workload.module.clean(context)
                        workload.state = WorkloadState.DELETED
                    except:
                        workload.state = WorkloadState.ERROR
                        logger.exception('Error from customer workload {} clean'.format(
                            workload.name))
                workload.state = WorkloadState.DELETED

    def _clean_resources(self):
        logger.info('Clean resources')
        for resource in self.experiment.resources.itervalues():
            logger.info('Clean resource {}'.format(resource.name))
            with self.experiment.workspace.cwd():
                context = Context(resource, self.experiment)
                has_clean = False
                try:
                    getattr(resource.module, 'clean')
                    has_clean = True
                except:
                    logger.warning('Missing interface clean for {} resource'.format(
                        resource.name))
                if has_clean:
                    try:
                        resource.module.clean(context)
                        resource.state = ResourceState.DELETED
                    except:
                        resource.state = ResourceState.ERROR
                        logger.exception('Error from customer resource {} clean'.format(
                            resource.name))
                resource.state = ResourceState.DELETED

    def _clean_experiment(self):
        logger.info('Clean experiment')
        self.report_collector.write_report()


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
        self.template_dir = os.path.join(self.template_dir, '../templates')
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
        self.template_dir = os.path.join(self.template_dir, '../templates')
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
