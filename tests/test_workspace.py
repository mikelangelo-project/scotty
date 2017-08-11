import unittest
import mock

from scotty.core.workspace import Workspace, ExperimentWorkspace
from scotty.core.components import Component, Workload
from scotty.core.exceptions import ScottyException, ExperimentException


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self._workspace = Workspace('.')

    def test_config_path(self):
        self._workspace.config_path = '.'
        workspace_path = self._workspace.config_path
        self.assertEquals(workspace_path, '.')

    def test_factory(self):
        component = Component()
        with self.assertRaises(ScottyException):
            Workspace.factory(component, '.')


class ExperimentWorkspaceTest(unittest.TestCase):
    def setUp(self):
        self._workspace = ExperimentWorkspace('.')

    def test_config_path(self):
        self._workspace.config_path = '.'
        with self.assertRaises(ScottyException):
            self._workspace.config_path

    @mock.patch('os.path.isdir')
    @mock.patch('os.mkdir')
    def test_create_paths(self, mkdir_mock, isdir_mock):
        isdir_mock.return_value = False
        self._workspace.create_paths()
        self.assertEquals(4, mkdir_mock.call_count)

    def test_get_component_path(self):
        component = Component()
        with self.assertRaises(ExperimentException):
            self._workspace.get_component_path(component)

    @mock.patch('os.path.isdir')
    @mock.patch('os.mkdir')
    def test_create_component_path_on_demand(self, mkdir_mock, isdir_mock):
        workload = Workload()
        workload.config = {'name': 'test_workload'}
        isdir_mock.return_value = False
        self._workspace.workloads_path = '.'
        self._workspace.get_component_path(workload, True)
        mkdir_mock.assert_called_once()
