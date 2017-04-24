import logging
import os

import git

import scotty.utils as utils

logger = logging.getLogger(__name__)


class Workspace(object):
    def __init__(self, path, git_=None):
        self.path = path
        if git_ is None:
            self._git = git.cmd.Git
        else:
            self._git = git_


class Workflow(object):
    def __init__(self, options):
        self._options = options
        self.workspace = None

    def run(self):
        self._prepare()
        self._checkout()
        self._load()
        self._run()

    def _prepare(self):
        path = os.path.abspath(self._options.workspace)
        self.workspace = self.workspace or Workspace(path)

    def _checkout(self):
        if self._options.skip_checkout:
            return
        try:
            project = self._options.project or os.environ['ZUUL_PROJECT']
            zuul_url = self._options.zuul_url or os.environ['ZUUL_URL']
            zuul_ref = self._options.zuul_ref or os.environ['ZUUL_REF']
        except KeyError as e:
            message = 'Missing Zuul settings ({})'.format(e)
            logger.error(message)
            raise CheckoutException(message)
                
    def _load(self):
        pass

    def _run(self):
        pass

class CheckoutException(Exception):
    pass
