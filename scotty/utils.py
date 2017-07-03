import logging
import os

logger = logging.getLogger(__name__)

 
class ExperimentHelper(object):
    def __init__(self, context):
        self.context = context
        self.__experiment = context.v1._ContextV1__experiment

    def open_file(self, rel_path):
        if os.path.isabs(rel_path):
            raise ScottyException('Path for experiment file must be relative'. format(rel_path))
        with open(rel_path, 'r') as f:
            return f

    def get_resource(self, resource_name):
        resource = self.__experiment.resources.get(resource_name, None)
        if not resource:
            raise ScottyException('Can not find resource ({})'.format(resource_name))
        return resource
