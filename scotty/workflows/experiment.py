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
        resource_deploy_executor = ResourceDeployExecutor(self.experiment)
        resource_deploy_executor.submit_resources()
        resource_deploy_executor.collect_endpoints()

    def _run_systemcollectors(self):
        if self.experiment.has_errors():
            logger.info('Skip systemcollectors - something went wrong before')
            return
        logger.info('Run systemcollectors')
        systemcollector_collect_executor = SystemCollectorCollectExecutor(self.experiment)
        systemcollector_collect_executor.submit_systemcollectors()
        systemcollector_collect_executor.wait()

    def _run_workloads(self):
        if self.experiment.has_errors():
            logger.info('Skip workloads - something went wrong before')
            return
        logger.info('Run workloads')
        workload_run_executor = WorkloadRunExecutor(self.experiment)
        workload_run_executor.submit_workloads()
        workload_run_executor.collect_results()
        workload_collect_executor = WorkloadCollectExecutor(self.experiment)
        workload_collect_executor.submit_workloads()
        workload_collect_executor.wait()

    def _run_resultstores(self):
        logger.info('Run resultstore')
        resultstore_submit_executor = ResultStoreSubmitExecutor(self.experiment)
        resultstore_submit_executor.submit_resultstores()
        resultstore_submit_executor.wait()

    def _clean(self):
        self._clean_workloads()
        self._clean_resources()
        self._clean_experiment()

    def _clean_workloads(self):
        logger.info('Clean workloads')
        workload_clean_executor = WorkloadCleanExecutor(self.experiment)
        workload_clean_executor.submit_workloads()
        workload_clean_executor.wait()

    def _clean_resources(self):
        logger.info('Clean resources')
        resources_clean_executor = ResourceCleanExecutor(self.experiment)
        resources_clean_executor.submit_resources()
        resources_clean_executor.wait()

    def _clean_experiment(self):
        if self.experiment.has_errors():
            sys.exit(1)

class ExperimentCleanWorkflow(Workflow):
    def _prepare(self):
        self.experiment = ExperimentFactory.build(self._options.workspace)

    def _run(self):
        msg = ('Delete scotty path ({})')
        logger.info(msg.format(self.experiment.workspace.scotty_path))
        shutil.rmtree(self.experiment.workspace.scotty_path)
    
    def _clean(self):
        pass
