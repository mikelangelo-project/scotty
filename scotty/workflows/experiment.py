import logging

from scotty.workflows.base import Workflow
from scotty.core.components import ExperimentFactory
from scotty.core.components import ResourceFactory
from scotty.core.components import WorkloadFactory
from scotty.core.executor import ResourceDeployExecutor, ResourceCleanExecutor
from scotty.core.executor import WorkloadRunExecutor, WorkloadCleanExecutor

logger = logging.getLogger(__name__)

class ExperimentPerformWorkflow(Workflow):
    def _prepare(self):
        self._prepare_experiment()
        self._prepare_resources()
        self._prepare_workloads()

    def _prepare_experiment(self):
        logger.info('Prepare experiment')
        self.experiment = ExperimentFactory.build(self._options)

    def _prepare_resources(self):
        logger.info('Prepare resources')
        resources_config =  self.experiment.config.get('resources', [])
        resources = map(self._prepare_resource, resources_config)
        map(self.experiment.add_component, resources)

    def _prepare_resource(self, resource_config):
        msg = 'Prepare resource {} ({})'
        logger.info(msg.format(resource_config['name'], resource_config['generator']))
        resource = ResourceFactory.build(resource_config, self.experiment)
        return resource
                                                     
    def _prepare_workloads(self):
        logger.info('Prepare workloads')
        workload_configs = self.experiment.config.get('workloads', [])
        workloads = map(self._prepare_workload, workload_configs)
        map(self.experiment.add_component, workloads)

    def _prepare_workload(self, workload_config):
        msg = 'Prepare workload {} ({})'
        logger.info(msg.format(workload_config['name'], workload_config['generator']))
        workload = WorkloadFactory.build(workload_config, self.experiment)
        return workload

    def _run(self):
        self._run_resources()
        self._run_static_report()
        self._run_workloads()
        self._run_result_store()

    def _run_resources(self):
        logger.info('Deploy resources')
        resource_deploy_executor = ResourceDeployExecutor()
        resource_deploy_executor.submit_resources(self.experiment.resources, self.experiment)
        resource_deploy_executor.collect_endpoints()

    def _run_static_report(self):
        pass

    def _run_workloads(self):
        logger.info('Run workloads')
        workload_run_executor = WorkloadRunExecutor()
        workload_run_executor.submit_workloads(self.experiment.workloads, self.experiment)
        workload_run_executor.collect_results()

    def _run_result_store(self):
        pass

    def _clean(self):
        self._clean_workloads()
        self._clean_resources()
        self._clean_experiment()

    def _clean_workloads(self):
        logger.info('Clean workloads')
        workload_clean_executor = WorkloadCleanExecutor()
        workload_clean_executor.submit_workloads(self.experiment.workloads, self.experiment)
        workload_clean_executor.wait()

    def _clean_resources(self):
        logger.info('Clean resources')
        resources_clean_executor = ResourceCleanExecutor()
        resources_clean_executor.submit_resources(self.experiment.resources, self.experiment)
        resources_clean_executor.wait()

    def _clean_experiment(self):
        pass
