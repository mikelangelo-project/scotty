import logging
import os
from contextlib import contextmanager

from scotty.core.exceptions import ScottyException

logger = logging.getLogger(__name__)


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
