import unittest
import yaml
import sys
import imp
import os

import mock

from scotty.core.components import Workload
from scotty.core.components import Experiment
from scotty.core.context import Context
from scotty.core.workspace import WorkloadWorkspace
from scotty.core.exceptions import WorkloadException 
from scotty.cli import Cli


class WorkloadTest(unittest.TestCase):
    workload_path = 'samples/components/workload/demo/workload_gen.py'
    workspace_path = 'samples/components/workload/demo/'

    def setUp(self):
        self._workspace = WorkloadWorkspace(self.workspace_path)


class WorkloadWorkspaceTest(WorkloadTest):
    def test_module_path(self):
        workload = Workload()
        workload.workspace = self._workspace 
        module_path = workload.module_path
        self.assertEquals(module_path, os.path.abspath('samples/components/workload/demo/workload_gen.py'))

    def test_cwd(self):
        with self._workspace.cwd():
            wd = os.getcwd()
        workspace_path = os.path.abspath(self.workspace_path)
        self.assertEquals(wd, workspace_path)
