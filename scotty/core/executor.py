import logging
import pickle
from datetime import datetime

from concurrent import futures

#from concurrent.futures import ProcessPoolExecutor, as_completed
#from concurrent.futures import wait as futures_wait

from scotty.core.checkout import CheckoutManager
from scotty.core.moduleloader import ModuleLoader
from scotty.core.components import CommonComponentState
from scotty.core.exceptions import ScottyException
from scotty.core.context import Context


logger = logging.getLogger(__name__)


def exec_component(experiment, component, interface_, result_interface):
    logger.info('Execute {} {} for {}'.format(component.type, interface_, component.name))
    component_task = ComponentTask(experiment, component, interface_)
    result = component_task.run()
    if result_interface:
        setattr(component, result_interface, result)
    return component


class ComponentTask(object):
    def __init__(self, experiment, component, interface_):
        CheckoutManager.populate(component, experiment.workspace.path)
        self.experiment = experiment
        self.component = component
        self.component_module =  ModuleLoader.load_by_component(component)
        self.interface_ = interface_

    def run(self):
        with self.experiment.workspace.cwd():
            context = Context(self.component, self.experiment)
            function_ = self._get_function()
            result = self._exec_function(function_, context)
            if self.component.state == CommonComponentState.ERROR:
                self.experiment.state = CommonComponentState.ERROR
            return result

    def _get_function(self):
        try:
            function_ = getattr(self.component_module, self.interface_)
            return function_
        except:
            msg = 'Missing interface {} {}.{}'.format(
                self.component.type, 
                self.component.name, 
                self.interface_)
            raise ScottyException(msg)

    def _exec_function(self, function_, context):
        try:
            self.component.state = CommonComponentState.ACTIVE
            self.component.starttime = datetime.now()
            result = function_(context)
            self.component.endtime = datetime.now()
            self.component.state = CommonComponentState.COMPLETED
            return result
        except:
            self._log_component_exception()

    def _log_component_exception(self):
        self.component.state = CommonComponentState.ERROR
        msg = 'Error from customer {}.{}'.format(self.component.type, self.component.name)
        logger.exception(msg) 

class ComponentExecutor(futures.ProcessPoolExecutor):
    def __init__(self):
        super(ComponentExecutor, self).__init__(max_workers=4)
        self._future_to_component = {}

    def submit(self, experiment, component, interface_, result_interface=None):
        future = super(ComponentExecutor, self).submit(
            exec_component, 
            experiment, 
            component, 
            interface_, 
            result_interface)
        self._future_to_component[future] = component
 
    def wait(self):
        for future in futures.as_completed(self._future_to_component):
            exception = future.exception()
            if exception:
                logger.error(exception)

    def copy_task_attributes(self, source_component, target_component, result_interface=None):
        target_component.starttime = source_component.starttime
        target_component.endtime = source_component.endtime
        target_component.state = source_component.state
        if result_interface:
            result = getattr(source_component, result_interface)
            setattr(target_component, result_interface, result)


class WorkloadRunExecutor(ComponentExecutor):
    def submit_workloads(self, experiment):
        workloads = experiment.components['workload']
        for workload in workloads.itervalues():
            logger.info('Submit workload {}.run(context)'.format(workload.name))
            self.submit(experiment, workload, 'run', result_interface="result")

    def collect_results(self):
        for future in futures.as_completed(self._future_to_component):
            workload = self._future_to_component[future]
            workload_future = future.result()
            self.copy_task_attributes(workload_future, workload, result_interface="result")


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
            self.submit(experiment, resource, 'deploy', result_interface="endpoint")

    def collect_endpoints(self):
        for future in futures.as_completed(self._future_to_component):
            resource = self._future_to_component[future]
            resource_future = future.result()
            self.copy_task_attributes(resource_future, resource, result_interface="endpoint")


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
            self.submit(experiment, systemcollector, 'collect', result_interface="result")

    def collect_results(self):
        for future in futures.as_completed(self._future_to_component):
            systemcollector = self._future_to_component[future]
            systemcollector_future = future.result()
            self.copy_task_attributes(systemcollector_future, systemcollector, result_interface="result")


class ResultStoreSubmitExecutor(ComponentExecutor):
    def submit_resultstores(self, experiment):
        resultstores = experiment.components['resultstore']
        for resultstore in resultstores.itervalues():
            msg = 'Submit resultstore {}.submit(context)'
            logger.info(msg.format(resultstore.name))
            self.submit(experiment, resultstore, 'submit')
