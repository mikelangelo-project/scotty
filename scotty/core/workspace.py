import os
import contextlib


class Workspace(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)

    @contextlib.contextmanager
    def cwd(self):
        prev_cwd = os.getcwd()
        os.chdir(self.path)
        yield
        os.chdir(prev_cwd)


class ExperimentWorkspace(Workspace):
    pass


class WorkloadWorkspace(Workspace):
    pass


class ResourceWorkspace(Workspace):
    pass
