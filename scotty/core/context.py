import logging

logger = logging.getLogger(__name__)


class BaseContext(object):
    def __getattr__(self, name):
        return self._context[name]


class Context(BaseContext):
    def __init__(self, self_component, experiment=None):
        self._context = {}
        self._context['v1'] = ContextV1(self_component, experiment)


class ContextV1(BaseContext):
    def __init__(self, self_component, experiment=None):
        self._context = {}
        self._context['self'] = self_component
        self._context['experiment'] = experiment
        self._init_utils()

    def _init_utils(self):
        self._context['utils'] = None #osmod heat etc
