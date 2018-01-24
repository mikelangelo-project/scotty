import logging
from datetime import datetime
import shutil
import sys

from scotty.workflows.base import Workflow
from scotty.core.components import ExperimentFactory
from scotty.core.components import ResourceFactory
from scotty.core.components import WorkloadFactory
from scotty.core.components import SystemCollectorFactory
from scotty.core.components import ResultStoreFactory
from scotty.core.executor import ResourceDeployExecutor, ResourceCleanExecutor
from scotty.core.executor import WorkloadRunExecutor, WorkloadCollectExecutor, WorkloadCleanExecutor
from scotty.core.executor import SystemCollectorCollectExecutor
from scotty.core.executor import ResultStoreSubmitExecutor

logger = logging.getLogger(__name__)

class ExperimentPerformWorkflow(Workflow):
    def _prepare(self):
        logger.info('Prepare experiment')
        self.experiment = ExperimentFactory.build(self._options.workspace, self._options.config)
        self.experiment.starttime = datetime.now()

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
        workload_collect_executor = WorkloadCollectExecutor()
        workload_collect_executor.submit_workloads(self.experiment)
        workload_collect_executor.wait()

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
        if self.experiment.has_errors():
            sys.exit(1)

class ExperimentCleanWorkflow(Workflow):
    def _prepare(self):
        self.experiment = ExperimentFactory.build(self._options)

    def _run(self):
        msg = ('Delete scotty path ({})')
        logger.info(msg.format(self.experiment.workspace.scotty_path))
        shutil.rmtree(self.experiment.workspace.scotty_path)
    
    def _clean(self):
        pass
