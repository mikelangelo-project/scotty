import logging

from concurrent.futures import ThreadPoolExecutor, as_completed

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
            function_ = self._get_function(component.module, interface_)
            self._exec_function(component, function_, context)

    def _get_function(self, module_, interface_):
        function_ = getattr(module_, interface_)
        return function_

    def _exec_function(self, component, function_, context):
        try:
            component.state = CommonComponentState.ACTIVE
            result = function_(context)
            component.state = CommonComponentState.COMPLETED
            return result
        except:
            self._handle_function_exception(component)

    def _handle_function_exception(self, component):
        component.state = CommonComponentState.ERROR
        msg = 'Error from customer {}.{}'.format(component.type, component.name)
        logger.exception(msg)
        raise ScottyException(msg)


class WorkloadRunExecutor(ComponentExecutor):
    def submit_workloads(self, workloads, experiment):
        for workload in workloads.itervalues():
            logger.info('Submit workload {}.run(context)'.format(workload.name))
            self.submit(experiment, workload, 'run')

    def collect_results(self):
        for future in as_completed(self._future_to_component):
            workload = self._future_to_component[future]
            workload.result = future.result()

class ResourceDeployExecutor(ComponentExecutor):
    def submit_resources(self, resources, experiment):
        for resource in resources.itervalues():
            logger.info('Submit resource {}.deploy(context)'.format(resource.name))
           
