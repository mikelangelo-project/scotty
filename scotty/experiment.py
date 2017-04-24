import logging

import git

import scotty.utils as utils

logger = logging.getLogger(__name__)


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self.workspace = None

    def run(self):
        logger.info('Run experiment.Workflow')
