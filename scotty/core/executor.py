import logging

from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import wait as futures_wait

from scotty.core.components import CommonComponentState
from scotty.core.exceptions import ScottyException
from scotty.core.context import Context

logger = logging.getLogger(__name__)


class ComponentExecutor(ThreadPoolExecutor):
    def __init__(self):
        super(ComponentExecutor, self).__init__(4)
        self._future_to_component = {}

    def submit(self, experiment, component, interface_):
        future = super(ComponentExecutor, self).submit(
            self._exec_with_context, 
            experiment, 
            component, 
            interface_)
        self._future_to_component[future] = component

    def _exec_with_context(self, experiment, component, interface_):
        logger.info('Execute {} {} for {}'.format(component.type, interface_, component.name))
        with experiment.workspace.cwd():
            context = Context(component, experiment)
            function_ = self._get_function(component, interface_)
            result = self._exec_function(component, function_, context)
            return result

    def _get_function(self, component, interface_):
        try:
            function_ = getattr(component.module, interface_)
            return function_
        except:
            msg = 'Missing interface {} {}.{}'.format(component.type, component.name, interface_)
            raise ScottyException(msg)

    def _exec_function(self, component, function_, context):
        try:
            component.state = CommonComponentState.ACTIVE
            result = function_(context)
            component.state = CommonComponentState.COMPLETED
            return result
        except:
            self._log_component_exception(component)

    def _log_component_exception(self, component):
        component.state = CommonComponentState.ERROR
        msg = 'Error from customer {}.{}'.format(component.type, component.name)
        logger.exception(msg)

    def wait(self):
        for future in as_completed(self._future_to_component):
            exception = future.exception()
            if exception:
                logger.error(exception)


class WorkloadRunExecutor(ComponentExecutor):
    def submit_workloads(self, experiment):
        workloads = experiment.components['workload']
        for workload in workloads.itervalues():
            logger.info('Submit workload {}.run(context)'.format(workload.name))
            self.submit(experiment, workload, 'run')

    def collect_results(self):
        for future in as_completed(self._future_to_component):
            workload = self._future_to_component[future]
            workload.result = future.result()


class WorkloadCleanExecutor(ComponentExecutor):
    def submit_workloads(self, experiment):
        workloads = experiment.components['workload']
        for workload in workloads.itervalues():
            logger.info('Submit workload {}.clean(context)'.format(workload.name))
            self.submit(experiment, workload, 'clean')


class ResourceDeployExecutor(ComponentExecutor):
    def submit_resources(self, experiment):
        resources = experiment.components['resource']
        for resource in resources.itervalues():
            logger.info('Submit resource {}.deploy(context)'.format(resource.name))
            self.submit(experiment, resource, 'deploy')

    def collect_endpoints(self):
        for future in as_completed(self._future_to_component):
            resource = self._future_to_component[future]
            resource.endpoint = future.result() 


class ResourceCleanExecutor(ComponentExecutor):
    def submit_resources(self, experiment):
        resources = experiment.components['resource']
        for resource in resources.itervalues():
            logger.info('Submit resource {}.clean(context)'.format(resource.name))
            self.submit(experiment, resource, 'clean')


class SystemCollectorCollectExecutor(ComponentExecutor):
    def submit_systemcollectors(self, experiment):
        systemcollectors = experiment.components['systemcollector']
        for systemcollector in systemcollectors.itervalues():
            msg = 'Submit systemcollector {}.collect(context)'
            logger.info(msg.format(systemcollector.name))
            self.submit(experiment, systemcollector, 'collect')

    def collect_results(self):
        for future in as_completed(self._future_to_component):
            systemcollector = self._future_to_component[future]
            systemcollector.result = future.result()


class ResultStoreSubmitExecutor(ComponentExecutor):
    def submit_resultstores(self, experiment):
        resultstores = experiment.components['resultstore']
        for resultstore in resultstores.itervalues():
            msg = 'Submit resultstore {}.submit(context)'
            logger.info(msg.format(resultstore.name))
            self.submit(experiment, resultstore, 'submit')
