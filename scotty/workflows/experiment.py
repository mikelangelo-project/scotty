import logging

from scotty.workflows.base import Workflow
from scotty.core.components import ExperimentFactory
from scotty.core.components import ResourceFactory
from scotty.core.components import WorkloadFactory
from scotty.core.components import SystemCollectorFactory
from scotty.core.components import ResultStoreFactory
from scotty.core.executor import ResourceDeployExecutor, ResourceCleanExecutor
from scotty.core.executor import WorkloadRunExecutor, WorkloadCleanExecutor
from scotty.core.executor import SystemCollectorCollectExecutor
from scotty.core.executor import ResultStoreSubmitExecutor

logger = logging.getLogger(__name__)

class ExperimentPerformWorkflow(Workflow):
    def _prepare(self):
        self._prepare_experiment()
        self._prepare_resources()
        self._prepare_systemcollectors()
        self._prepare_workloads()
        self._prepare_resultstores()

    def _prepare_experiment(self):
        logger.info('Prepare experiment')
        self.experiment = ExperimentFactory.build(self._options)

    def _prepare_resources(self):
        logger.info('Prepare resources')
        resource_configs = self.experiment.config.get('resources', [])
        resources = map(self._prepare_resource, resource_configs)
        map(self.experiment.add_component, resources)

    def _prepare_resource(self, resource_config):
        msg = 'Prepare resource {} ({})'
        logger.info(msg.format(resource_config['name'], resource_config['generator']))
        resource = ResourceFactory.build(resource_config, self.experiment)
        return resource
                                                     
    def _prepare_systemcollectors(self):
        logger.info('Prepare systemcollectors')
        systemcollector_configs = self.experiment.config.get('systemcollectors', [])
        systemcollectors = map(self._prepare_systemcollector, systemcollector_configs)
        map(self.experiment.add_component, systemcollectors)

    def _prepare_systemcollector(self, systemcollector_config):
        msg = 'Prepare systemcollector {} ({})'
        logger.info(msg.format(systemcollector_config['name'], systemcollector_config['generator']))
        systemcollector = SystemCollectorFactory.build(systemcollector_config, self.experiment)
        return systemcollector

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

    def _prepare_resultstores(self):
        logger.info('Prepare resultstores')
        resultstore_configs = self.experiment.config.get('resultstores', [])
        resultstores = map(self._prepare_resultstore, resultstore_configs)
        map(self.experiment.add_component, resultstores)

    def _prepare_resultstore(self, resultstore_config):
        msg = 'Prepare resultstore {} ({})'
        logger.info(msg.format(resultstore_config['name'], resultstore_config['generator']))
        resultstore = ResultStoreFactory.build(resultstore_config, self.experiment)
        return resultstore

    def _run(self):
        self._run_resources()
        self._run_systemcollectors()
        self._run_workloads()
        self._run_resultstores()

    def _run_resources(self):
        logger.info('Deploy resources')
        resource_deploy_executor = ResourceDeployExecutor()
        resource_deploy_executor.submit_resources(self.experiment)
        resource_deploy_executor.collect_endpoints()

    def _run_systemcollectors(self):
        logger.info('Run systemcollectors')
        systemcollector_collect_executor = SystemCollectorCollectExecutor()
        systemcollector_collect_executor.submit_systemcollectors(self.experiment)
        systemcollector_collect_executor.wait()

    def _run_workloads(self):
        logger.info('Run workloads')
        workload_run_executor = WorkloadRunExecutor()
        workload_run_executor.submit_workloads(self.experiment)
        workload_run_executor.collect_results()

    def _run_resultstores(self):
        logger.info('Run resultstore')
        resultstore_submit_executor = ResultStoreSubmitExecutor()
        resultstore_submit_executor.submit_resultstores(self.experiment)
        resultstore_submit_executor.wait()

    def _clean(self):
        self._clean_workloads()
        self._clean_resources()
        self._clean_experiment()

    def _clean_workloads(self):
        logger.info('Clean workloads')
        workload_clean_executor = WorkloadCleanExecutor()
        workload_clean_executor.submit_workloads(self.experiment)
        workload_clean_executor.wait()

    def _clean_resources(self):
        logger.info('Clean resources')
        resources_clean_executor = ResourceCleanExecutor()
        resources_clean_executor.submit_resources(self.experiment)
        resources_clean_executor.wait()

    def _clean_experiment(self):
        pass
