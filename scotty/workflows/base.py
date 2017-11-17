import logging

from scotty.config import ScottyConfig

logger = logging.getLogger(__name__)


class Workflow(object):
    def __init__(self, options):
        self._options = options
        
    def run(self):
        self._prepare()
        self._run()
        self._clean()

    def _prepare(self):
        msg = '_prepare(self) must be implemented'
        raise NotImplementedError(msg)

    def _run(self):
        msg = '_run(self) must be implemented'
        raise NotImplementedError(msg)

    def _clean(self):
        msg = '_clean(self) must be implemented'
        raise NotImplementedError(msg)
