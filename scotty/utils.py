import logging
import os
from contextlib import contextmanager

from scotty.core.exceptions import ScottyException

logger = logging.getLogger(__name__)


class BaseUtils(object):
    def __init__(self, context):
        self.context = context
        self.__experiment = context.v1._ContextV1__experiment

    @property
    def experiment_uuid(self):
        return self.__experiment.uuid

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
        experiment_workspace = self._BaseUtils__experiment.workspace
        self.component_data_path = experiment_workspace.get_component_data_path(self.current_workload, True)

    def _real_path(self, file_):
        file_ = os.path.basename(os.path.normpath(file_))
        real_path = "{}/{}".format(self.component_data_path, file_)
        return real_path

    def open_file(self, file_, mode):
        real_path = self._real_path(file_)
        return open(real_path, mode)

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
