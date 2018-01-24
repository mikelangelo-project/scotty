import logging
import os
import sys
import yaml
import re
import uuid
from collections import defaultdict

from aenum import Enum

from scotty.core.checkout import CheckoutManager
from scotty.core.moduleloader import ModuleLoader
from scotty.core.context import ContextAccessible
from scotty.core.exceptions import ExperimentException
from scotty.core.exceptions import ScottyException
from scotty.core.workspace import Workspace, ExperimentWorkspace
from scotty.core import settings

logger = logging.getLogger(__name__)


class CommonComponentState(Enum):
    PREPARE = 0
    ACTIVE = 1
    COMPLETED = 2
    DELETED = 3
    ERROR = 4


class Component(object):
    def __init__(self):
        self.uuid = uuid.uuid4()
        self.config = None
        self.workspace = None
        self.starttime = None
        self.endtime = None
        self._generator = None
        self._setaccess('uuid')
        self._setaccess('config')
        self._setaccess('name')
        self._setaccess('starttime')
        self._setaccess('endtime')
        self._setaccess('type')

    def _setaccess(self, parameter):
        ContextAccessible(self.__class__.__name__).setaccess(parameter)

    @property
    def name(self):
        return self.config['name']

    def issource(self, type_):
        source_type = self.get_source_type()
        same_type = source_type == type_.upper()
        return same_type

    def _parse_generator(self):
        pattern_source_str = re.compile(r'(git|file):([^\[]+)(?:\[([^\]]+)\])?$')
        source_str = self.config['generator']
        groups = pattern_source_str.match(source_str).groups()
        self._generator = {
            "type":groups[0],
            "location":groups[1],
            "reference":groups[2]
        }

    @property
    def generator(self):
        if not self._generator:
            self._parse_generator()
        return self._generator

    def get_source_type(self):
        source = self.config['generator'].split(':')
        source_type = source[0].upper()
        return source_type

    def isinstance(self, type_str):
        class_ = getattr(sys.modules[__name__], type_str)
        return isinstance(self, class_)

    @property
    def type(self):
        type_ = self.__class__.identifier()
        return type_

    @classmethod
    def identifier(cls, plural=False):
        identifier = cls.__name__
        if plural:
            identifier = "{}s".format(identifier)
        identifier = identifier.lower()
        return identifier

    @classmethod
    def factory(cls):
        component_factory_str = "{}Factory".format(cls.__name__)
        component_factory = getattr(sys.modules[__name__], component_factory_str)
        return component_factory

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
        self.state = CommonComponentState.PREPARE
        
    def add_component(self, component):
        if component.type in ExperimentWorkspace.supported_components:
            self.components[component.type][component.name] = component
        else:
            raise ExperimentException(
                'Component {} cannot add to experiment'.format(
                    component.type))

    def has_errors(self):
        return self.state == CommonComponentState.ERROR


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
        self._setaccess('params')
        
    @property
    def params(self):
        return self.config['params']

    @property
    def module_path(self):
        return os.path.join(self.workspace.path, 'resultstore.py')


class ComponentValidator(object):
    @classmethod
    def validate_interfaces(cls, component):
        pass
        for interface_ in component.module_interfaces:
            cls.validate_interface(component, interface_)

    @classmethod
    def validate_interface(cls, component, interface_):
        pass
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

    @classmethod
    def _build_from_experiment(cls, experiment, component_class):
        component_configs = experiment.config.get(component_class.identifier(True), [])
        component_factory = component_class.factory()
        build = lambda component_config: component_factory.build(component_config, experiment)
        components = map(build, component_configs)
        return components
        

class ExperimentFactory(ComponentFactory):
    yaml_pattern_env = re.compile(r'\<%=\s*ENV\[\'([^\]\s]+)\'\]\s*%\>')
    @classmethod
    def build(cls, workspace_path, cfg_path=None):
        experiment = Experiment()
        experiment.workspace = Workspace.factory(experiment, workspace_path, True)
        experiment.workspace.config_path = cls._get_experiment_config_path(experiment, cfg_path)
        experiment.config = cls._get_experiment_config(experiment)
        cls._build_components(experiment)
        return experiment

    @classmethod
    def _build_components(cls, experiment):
        resources = cls._build_from_experiment(experiment, Resource)
        workloads = cls._build_from_experiment(experiment, Workload)
        systemcollectors = cls._build_from_experiment(experiment, SystemCollector)
        resultstores = ResultStoreFactory.build_from_settings(experiment)
        map(experiment.add_component, resources)
        map(experiment.add_component, workloads)
        map(experiment.add_component, systemcollectors)
        map(experiment.add_component, resultstores)

    @classmethod
    def _get_experiment_config_path(cls, experiment, config_path):
        config_path = config_path or experiment.workspace.config_path
        return config_path

    @classmethod
    def _get_experiment_config(cls, experiment):
         with open(experiment.workspace.config_path, 'r') as stream:
             yaml.add_implicit_resolver ( "!scotty_yaml_env", cls.yaml_pattern_env )
             yaml.add_constructor('!scotty_yaml_env', cls._scotty_yaml_env_constructor)
             config = yaml.load(stream)
         return config

    @classmethod
    def _scotty_yaml_env_constructor(cls, loader, node):
        value = loader.construct_scalar(node)
        env_var = cls.yaml_pattern_env.match(value).groups()[0]
        return os.environ.get(env_var, '')

class ResourceFactory(ComponentFactory):
    @classmethod
    def build(cls, resource_config, experiment):
        logger.info("Build Resource")
        resource = Resource()
        resource.config = resource_config
        resource.workspace = cls._get_component_workspace(experiment, resource)
        return resource

class SystemCollectorFactory(ComponentFactory):
    @classmethod
    def build(cls, systemcollector_config, experiment):
        systemcollector = SystemCollector()
        systemcollector.config = systemcollector_config
        systemcollector.workspace = cls._get_component_workspace(experiment, systemcollector)
        return systemcollector

class WorkloadFactory(ComponentFactory):
    @classmethod
    def build(cls, workload_config, experiment):
        workload = Workload()
        workload.config = workload_config
        workload.workspace = cls._get_component_workspace(experiment, workload)
        return workload

class ResultStoreFactory(ComponentFactory):
    @classmethod
    def build(cls, resultstore_config, experiment):
        resultstore = ResultStore()
        resultstore.config = resultstore_config
        resultstore.workspace = cls._get_component_workspace(experiment, resultstore)
        return resultstore

    @classmethod
    def build_from_settings(cls, experiment):
        resultstores = []
        setting_resultstores = settings.get('resultstores', 'stores')
        for setting_resultstore in setting_resultstores:
            enable = settings.get(setting_resultstore, 'enable')
            if not enable:
                continue 
            resultstore_config = {}
            resultstore_config['name'] = setting_resultstore
            resultstore_config['generator'] = settings.get(setting_resultstore, 'generator')
            resultstore_config['params'] = settings.get(setting_resultstore, 'params')
            resultstore = cls.build(resultstore_config, experiment)
            resultstores.append(resultstore)
        return resultstores
