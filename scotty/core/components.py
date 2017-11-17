import logging
import os
import sys
import yaml
from collections import defaultdict

from aenum import Enum

from scotty.core.checkout import CheckoutManager
from scotty.core.moduleloader import ModuleLoader
from scotty.core.context import ContextAccessible
from scotty.core.exceptions import ExperimentException
from scotty.core.exceptions import ScottyException
from scotty.core.workspace import Workspace, ExperimentWorkspace

logger = logging.getLogger(__name__)


class CommonComponentState(Enum):
    PREPARE = 0
    ACTIVE = 1
    COMPLETED = 2
    DELETED = 3
    ERROR = 4


class Component(object):
    def __init__(self):
        self.config = None
        self.workspace = None
        self.starttime = None
        self.endtime = None
        self._setaccess('config')
        self._setaccess('name')
        self._setaccess('starttime')
        self._setaccess('endtime')

    def _setaccess(self, parameter):
        ContextAccessible(self.__class__.__name__).setaccess(parameter)

    @property
    def name(self):
        return self.config['name']

    def issource(self, type_):
        source = self.config['generator'].split(':')
        source_type = source[0].upper()
        same_type = source_type == type_.upper()
        return same_type

    def isinstance(self, type_str):
        class_ = getattr(sys.modules[__name__], type_str)
        return isinstance(self, class_)

    @property
    def type(self):
        type_ = self.__class__.__name__
        return type_.lower()


class WorkloadState(Enum):
    PREPARE = 0
    ACTIVE = 1
    COMPLETED = 2
    DELETED = 3
    ERROR = 4


class Workload(Component):
    module_interfaces = [
        'run',
    ]

    def __init__(self):
        super(Workload, self).__init__()
        self.module = None
        self.parent_module_name = 'scotty.workload'
        self.state = WorkloadState.PREPARE
        self.result = None
        self._setaccess('params')
        self._setaccess('resources')
        self._setaccess('result')

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'workload_gen.py')

    @property
    def params(self):
        return self.config['params']

    @property
    def resources(self):
        return self.config['resources']


class Experiment(Component):
    def __init__(self):
        super(Experiment, self).__init__()
        self.components = defaultdict(dict)

    def add_component(self, component):
        if component.type in ExperimentWorkspace.supported_components:
            self.components[component.type][component.name] = component
        else:
            raise ExperimentException(
                'Component {} cannot add to experiment'.format(
                    component.type))


class ResourceState(Enum):
    PREPARE = 0
    ACTIVE = 1
    COMPLETED = 2
    DELETED = 3
    ERROR = 4

 
class Resource(Component):
    module_interfaces = [
        'deploy',
        'clean',
    ]
    def __init__(self):
        super(Resource, self).__init__()
        self.module = None
        self.parent_module_name = 'scotty.resource'
        self.state = CommonComponentState.PREPARE
        self.endpoint = None
        self._setaccess('params')
        self._setaccess('endpoint')

    @property
    def params(self):
        return self.config['params']

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'resource_gen.py')


class SystemCollector(Component):
    module_interfaces = [
        'collect',
    ]

    def __init__(self):
        super(SystemCollector, self).__init__()
        self.module = None
        self.parent_module_name = 'scotty.systemcollector'
        self.state = CommonComponentState.PREPARE
        self.result = None
        self._setaccess('result')
        
    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'systemcollector.py')


class ResultStore(Component):
    module_interfaces = [
        'submit',
    ]

    def __init__(self):
        super(ResultStore, self).__init__()
        self.module = None
        self.parent_module_name = 'scotty.resultstore'
        self.state = CommonComponentState.PREPARE

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'resultstore.py')


class ComponentValidator(object):
    @classmethod
    def validate_interfaces(cls, component):
        for interface_ in component.module_interfaces:
            cls.validate_interface(component, interface_)

    @classmethod
    def validate_interface(cls, component, interface_):
        try:
            getattr(component.module, interface_)
        except:
            err_msg = 'Missing interface {} for {} {}.'.format(
                interface_,
                component.type,
                component.name)
            raise ScottyException(err_msg)

class ComponentFactory(object):
    @classmethod
    def _get_component_workspace(cls, experiment, component):
        workspace_path = experiment.workspace.get_component_path(component)
        workspace = Workspace.factory(component, workspace_path)
        return workspace

    @classmethod
    def _get_component_module(cls, experiment, component):
        CheckoutManager.populate(component, experiment.workspace.path)
        module_ =  ModuleLoader.load_by_component(component)
        return module_

class ExperimentFactory(ComponentFactory):
    @classmethod
    def build(cls, options):
        experiment = Experiment()
        experiment.workspace = Workspace.factory(experiment, options.workspace, True)
        experiment.workspace.config_path = cls._get_experiment_config_path(experiment, options)
        experiment.config = cls._get_experiment_config(experiment)
        return experiment

    @classmethod
    def _get_experiment_config_path(cls, experiment, options):
        config = ''
        if hasattr(options, 'config'):
            config = options.config
        config_path = config or experiment.workspace.config_path
        return config_path

    @classmethod
    def _get_experiment_config(cls, experiment):
         with open(experiment.workspace.config_path, 'r') as stream:
             config = yaml.load(stream)
         return config


class ResourceFactory(ComponentFactory):
    @classmethod
    def build(cls, resource_config, experiment):
        resource = Resource()
        resource.config = resource_config
        resource.workspace = cls._get_component_workspace(experiment, resource)
        resource.module = cls._get_component_module(experiment, resource)
        return resource

class SystemCollectorFactory(ComponentFactory):
    @classmethod
    def build(cls, systemcollector_config, experiment):
        systemcollector = SystemCollector()
        systemcollector.config = systemcollector_config
        systemcollector.workspace = cls._get_component_workspace(experiment, systemcollector)
        systemcollector.module = cls._get_component_module(experiment, systemcollector)
        return systemcollector

class WorkloadFactory(ComponentFactory):
    @classmethod
    def build(cls, workload_config, experiment):
        workload = Workload()
        workload.config = workload_config
        workload.workspace = cls._get_component_workspace(experiment, workload)
        workload.module = cls._get_component_module(experiment, workload)
        return workload

class ResultStoreFactory(ComponentFactory):
    @classmethod
    def build(cls, resultstore_config, experiment):
        resultstore = ResultStore()
        resultstore.config = resultstore_config
        resultstore.workspace = cls._get_component_workspace(experiment, resultstore)
        resultstore.module = cls._get_component_module(experiment, resultstore)
        return resultstore
