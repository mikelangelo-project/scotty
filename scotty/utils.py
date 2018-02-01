import logging
import os
from time import sleep 
from contextlib import contextmanager

import keystoneauth1.loading
import keystoneauth1.session
import heatclient.client
from heatclient.common import template_utils

from scotty.core.exceptions import ScottyException

logger = logging.getLogger(__name__)


class BaseUtils(object):
    def __init__(self, context):
        self.context = context
        self.__experiment = context.v1._ContextV1__experiment

    @property
    def experiment_uuid(self):
        return self.__experiment.uuid

    @property
    def experiment_workspace(self):
        return self._BaseUtils__experiment.workspace

class ExperimentHelper(object):
    def __init__(self, context):
        # TODO validate context - is from scotty and not a fake from customer component
        self.context = context
        self.__experiment = context.v1._ContextV1__experiment

    @contextmanager
    def open_file(self, rel_path):
        if os.path.isabs(rel_path):
            raise ScottyException(
                'Path for experiment file must be relative'.format(rel_path))
        with open(rel_path, 'r') as f:
            yield f

    def get_resource(self, resource_name):
        resource = self.__experiment.components['resource'].get(resource_name, None)
        if not resource:
            raise ScottyException(
                'Can not find resource ({})'.format(resource_name))
        return resource

    # restrict function to a list of context types (component list)
    # @restrict_to(component, component2, ...)
    def get_workloads(self):
        workloads = self.__experiment.components['workload']
        return workloads

    def get_experiment_starttime(self):
        return self.__experiment.starttime

    def get_experiment_uuid(self):
        return self.__experiment.uuid


class WorkloadUtils(BaseUtils):
    def __init__(self, context):
        super(WorkloadUtils, self).__init__(context)
        try:
            self.current_workload = context.v1.workload
        except KeyError as e:
            logger.error('WorkloadUtils can only used in workload context')
            raise
        self.component_data_path = self.experiment_workspace.get_component_data_path(
            self.current_workload, 
            True)
        self._resources = {}

    def _real_path(self, file_):
        file_ = os.path.basename(os.path.normpath(file_))
        real_path = "{}/{}".format(self.component_data_path, file_)
        return real_path

    def open_file(self, file_, mode):
        real_path = self._real_path(file_)
        return open(real_path, mode)

    @property
    def resources(self):
        if not self._resources:
            workload_resources = self.current_workload.resources
            resource_components = self._BaseUtils__experiment.components['resource'] 
            for resource_key in workload_resources:
                resource_name = workload_resources[resource_key] 
                resource_component = resource_components.get(resource_name, None)
                if not resource_components:
                    msg = 'Can not find resource ({})'.format(resource_name)
                    raise ScottyException(msg)
                self._resources[resource_key] = resource_component
        return self._resources


class ResourceUtils(BaseUtils):
    def __init__(self, context):
        super(ResourceUtils, self).__init__(context)
        try:
            self.current_resource = context.v1.resource
        except KeyError as e:
            logger.error('ResourceUtils can only used in reource context')
            raise

    @property
    def heat_client(self):
        if not self._heat_client:
            self._heat_client = HeatClient()
        return self._heat_client


class ResultstoreUtils(BaseUtils):
    def __init__(self, context):
        super(ResultstoreUtils, self).__init__(context)
        try:
            self.current_resultstore = context.v1.resultstore
        except KeyError as e:
            logger.error('ResultStoreUtils can only used in resultstore context')
            raise

    @property
    def workloads(self):
        workloads = self._BaseUtils__experiment.components['workload']
        return workloads

    @property
    def remote_base_dir(self):
        return "scotty"

    @property
    def remote_experiment_dir(self):
        remote_experiment_dir = os.path.join(self.remote_base_dir, str(self.experiment_uuid))
        return remote_experiment_dir

    def local_result_dir(self, workload_name):
        local_result_dir = os.path.join('.scotty/data/workload', workload_name)
        return local_result_dir


class HeatClient(object):
    def __init__(self, session):
        self._heat = heatclient.client.Client('1', session=session)

    def create_stack(self, tpl_path, stack_name, params):
        stack_args = self._create_stack_args(tpl_path, stack_name, params)
        self._heat.stacks.create(**stack_args)

    def _create_stack_args(self, tpl_path, stack_name, params):
        tpl_files, tpl = template_utils.get_template_contents(tpl_path)
        args = {
            'stack_name':stack_name,
            'template':tpl,
            'files':tpl_files,
            'parameters': params,
        }
        return args

    def delete_stack(self, stack_name):
        self._heat.stacks.delete(stack_name)

    def wait_for_stack(self, stack_name, state_finish="CREATE_COMPLETE", state_error="CREATE_FAILED"):
        while True:
            logger.info('Wait for stack {}'.format(stack_name))
            stack = self._heat.stacks.get(stack_name)
            if stack.stack_status == state_finish:
                return
            if stack.stack_status == state_error:
                raise Exception('Stack failed')
            sleep(20)

    def get_stack(self, stack_name):
        stack = self._heat.stacks.get(stack_name)
        return stack

    def parse_outputs(self, stack):
        outputs = {}
        for output in stack.outputs:
            outputs[output['output_key']] = output['output_value']
        return outputs
