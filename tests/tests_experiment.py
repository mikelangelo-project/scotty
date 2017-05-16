import unittest
import os

import mock

from scotty.core.experiment import Workspace
from scotty.core.exceptions import ExperimentException


class ExperimentWorkspaceTest(unittest.TestCase):
    workspace_path = 'samples/component/experiment'

    def test_workspace_init(self):
        Workspace(self.workspace_path)

    @mock.patch('os.path.isfile', return_value=False)
    def test_workspace_no_config(self, isfile_mock):
        workspace = Workspace(self.workspace_path)
        with self.assertRaises(ExperimentException):
            workspace.config_path

    @mock.patch('os.path.isfile', return_value=True)
    def test_workspace_config_path(self, isfile_mock):
        workspace = Workspace(self.workspace_path)
        config_path = workspace.config_path
        self.assertEquals(config_path, 'samples/component/experiment/experiment.yaml')

    def test_workloads_path(self):
        workspace = Workspace(self.workspace_path)
        workloads_path = workspace.workloads_path
        self.assertEquals(workloads_path, 'samples/component/experiment/.workloads/')

    def test_cwd(self):
        workspace = Workspace(self.workspace_path)
        with workspace.cwd():
            wd = os.getcwd()
        cwd = os.getcwd()
        self.assertEquals(wd, cwd+'/samples/component/experiment')
