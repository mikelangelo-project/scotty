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
        self.experiment = experiment
        self.component = component
        self.interface_ = interface_
        self.populate_component()
        self.component_module =  self.load_component_module()

    def populate_component(self):
        try:
            CheckoutManager.populate(self.component, self.experiment.workspace.path)
        except:
            self._log_component_exception()

    def load_component_module(self):
        try:
            component_module =  ModuleLoader.load_by_component(self.component)
            return component_module
        except:
            self._log_component_exception()

    def run(self):
        if not self.component_module:
            return
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
    def __init__(self, experiment):
        super(ComponentExecutor, self).__init__(max_workers=4)
        self._future_to_component = {}
        self.experiment = experiment

    def submit(self, component, interface_, result_interface=None):
        future = super(ComponentExecutor, self).submit(
            exec_component, 
            self.experiment, 
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

    def check_error(self, component):
        if component.state == CommonComponentState.ERROR:
            self.experiment.state = CommonComponentState.ERROR


class WorkloadRunExecutor(ComponentExecutor):
    def submit_workloads(self):
        workloads = self.experiment.components['workload']
        for workload in workloads.itervalues():
            logger.info('Submit workload {}.run(context)'.format(workload.name))
            self.submit(workload, 'run', result_interface="result")

    def collect_results(self):
        for future in futures.as_completed(self._future_to_component):
            workload = self._future_to_component[future]
            workload_future = future.result()
            self.copy_task_attributes(workload_future, workload, result_interface="result")
            self.check_error(workload)


class WorkloadCollectExecutor(ComponentExecutor):
    def submit_workloads(self):
        workloads = self.experiment.components['workload']
        for workload in workloads.itervalues():
            logger.info('Submit workload {}.collect(context)'.format(workload.name))
            self.submit(workload, 'collect')


class WorkloadCleanExecutor(ComponentExecutor):
    def submit_workloads(self):
        workloads = self.experiment.components['workload']
        for workload in workloads.itervalues():
            logger.info('Submit workload {}.clean(context)'.format(workload.name))
            self.submit(workload, 'clean')


class ResourceDeployExecutor(ComponentExecutor):
    def submit_resources(self):
        resources = self.experiment.components['resource']
        for resource in resources.itervalues():
            logger.info('Submit resource {}.deploy(context)'.format(resource.name))
            self.submit(resource, 'deploy', result_interface="endpoint")

    def collect_endpoints(self):
        for future in futures.as_completed(self._future_to_component):
            resource = self._future_to_component[future]
            resource_future = future.result()
            self.copy_task_attributes(resource_future, resource, result_interface="endpoint")
            self.check_error(resource)


class ResourceCleanExecutor(ComponentExecutor):
    def submit_resources(self):
        resources = self.experiment.components['resource']
        for resource in resources.itervalues():
            logger.info('Submit resource {}.clean(context)'.format(resource.name))
            self.submit(resource, 'clean')


class SystemCollectorCollectExecutor(ComponentExecutor):
    def submit_systemcollectors(self):
        systemcollectors = self.experiment.components['systemcollector']
        for systemcollector in systemcollectors.itervalues():
            msg = 'Submit systemcollector {}.collect(context)'
            logger.info(msg.format(systemcollector.name))
            self.submit(systemcollector, 'collect', result_interface="result")

    def collect_results(self):
        for future in futures.as_completed(self._future_to_component):
            systemcollector = self._future_to_component[future]
            systemcollector_future = future.result()
            self.copy_task_attributes(systemcollector_future, systemcollector, result_interface="result")
            self.check_error(systemcollector)


class ResultStoreSubmitExecutor(ComponentExecutor):
    def submit_resultstores(self):
        resultstores = self.experiment.components['resultstore']
        for resultstore in resultstores.itervalues():
            msg = 'Submit resultstore {}.submit(context)'
            logger.info(msg.format(resultstore.name))
            self.submit(resultstore, 'submit')
