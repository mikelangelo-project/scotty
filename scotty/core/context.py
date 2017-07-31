import logging

from scotty.core.exceptions import ScottyException

logger = logging.getLogger(__name__)


class ContextAccessible(object):
    accessibles = {}

    def __init__(self, component_type):
        self.component_type = component_type.lower()
        if self.component_type not in ContextAccessible.accessibles:
            ContextAccessible.accessibles[self.component_type] = {}
        self.component_accessible = ContextAccessible.accessibles[self.component_type]

    def __call__(self, function_):
        self.component_accessible[function_.__name__] = True
        return function_

    def setaccess(self, attribute_name):
        self.component_accessible[attribute_name] = True

    def isaccessible(self, name):
        return self.component_accessible.get(name, False)


class Context(object):
    def __init__(self, component, experiment):
        self._context = {}
        self._context['v1'] = ContextV1(component, experiment)

    def __getattr__(self, name):
        return self._context[name]


class ContextV1(Context):
    def __init__(self, component, experiment):
        self._context = {}
        self._context[component.type] = ContextComponent(component)
        self.__experiment = experiment


class ContextComponent(Context):
    def __init__(self, component):
        self.__context_accessible = ContextAccessible(component.__class__.__name__)
        self.__component = component

    def __getattr__(self, name):
        if self.__context_accessible.isaccessible(name):
            return getattr(self.__component, name)
        else:
            raise ScottyException('{} not found'.format(name))
