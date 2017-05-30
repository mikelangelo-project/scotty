import unittest
import os

import mock

from scotty.core.experiment import Experiment
from scotty.core.experiment import Workspace
from scotty.core.experiment import ExperimentLoader
from scotty.core.experiment import ExperimentConfigLoader
from scotty.core.experiment import Workflow
from scotty.core.workload import Workload
from scotty.core.exceptions import ExperimentException


def mock_workspace(workspace_path='samples/components/experiment'):
    return Workspace(workspace_path)


class ExperimentWorkspaceTest(unittest.TestCase):
    @mock.patch('os.path.isdir', return_value=False)
    def test_failed_workspace_init(self, isdir_mock):
        with self.assertRaises(ExperimentException):
            mock_workspace()

    def test_workspace_init(self):
        mock_workspace()

    @mock.patch('os.path.isfile', return_value=False)
    def test_workspace_no_config(self, isfile_mock):
        workspace = mock_workspace()
        with self.assertRaises(ExperimentException):
            workspace.config_path

    @mock.patch('os.path.isfile', return_value=True)
    def test_workspace_config_path(self, isfile_mock):
        workspace = mock_workspace()
        config_path = workspace.config_path
        self.assertEquals(config_path,
                          'samples/components/experiment/experiment.yaml')

    def test_workloads_path(self):
        workspace = mock_workspace()
        workloads_path = workspace.workloads_path
        self.assertEquals(workloads_path,
                          'samples/components/experiment/.workloads/')

    def test_cwd(self):
        workspace = mock_workspace()
        with workspace.cwd():
            wd = os.getcwd()
        cwd = os.getcwd()
        self.assertEquals(wd, cwd + '/samples/components/experiment')


class ExperimentLoaderTest(unittest.TestCase):
    def setUp(self):
        self.workspace = mock_workspace()
        
    def test_load_from_workspace(self):
        workspace = self.workspace
        config = None
        experiment = ExperimentLoader.load_from_workspace(workspace, config)
        self.assertEquals(workspace, experiment.workspace)
        self.assertIsNone(experiment.config)

    @mock.patch('os.path.isdir', return_value=False)
    @mock.patch('os.mkdir')
    def test_create_workloads_dir(self, isdir_mock, mkdir_mock):
        workspace = self.workspace
        ExperimentLoader._create_workloads_dir(workspace=workspace)
        isdir_mock.assert_called_once()
        mkdir_mock.assert_called_once()


class ExperimentTest(unittest.TestCase):
    def test_add_workload(self):
        experiment = Experiment()
        workload = Workload()
        workload.config = {'name': 'test_name'}
        experiment.add_workload(workload)
        self.assertEquals(experiment.workloads['test_name'], workload)
        self.assertEquals(len(experiment.workloads), 1)


class ExperimentConfigLoaderTest(unittest.TestCase):
    def test_load_by_workspace(self):
        workspace = mock_workspace()
        config = ExperimentConfigLoader.load_by_workspace(workspace)
        self.assertTrue(isinstance(config, dict))


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self.workflow = Workflow(options=None)

    @mock.patch('scotty.core.experiment.Workflow._prepare')
    @mock.patch('scotty.core.experiment.Workflow._checkout')
    @mock.patch('scotty.core.experiment.Workflow._load')
    @mock.patch('scotty.core.experiment.Workflow._perform')
    def test_run(self, prepare_mock, checkout_mock, load_mock, run_mock):
        self.workflow.perform()
        prepare_mock.assert_called()
        checkout_mock.assert_called()
        load_mock.assert_called()
        run_mock.assert_called()

    def test_prepare(self):
        options_mock = mock.MagicMock(workspace='.')
        self.workflow._options = options_mock
        self.workflow._prepare()
        new_workspace = self.workflow.workspace
        workspace_path = new_workspace.path
        cwd = os.getcwd()
        self.assertEquals(workspace_path, cwd)

    def test_skip_checkout(self):
        options_mock = mock.MagicMock(skip_checkout=True)
        self.workflow._options = options_mock
        self.workflow._checkout()

    @mock.patch('os.environ', return_value='zuul_env')
    @mock.patch('scotty.core.checkout.CheckoutManager.checkout')
    def test_checkout(self, checkout_mock, environ_mock):
        options_mock = mock.MagicMock(
            project='test_project', skip_checkout=False)
        self.workflow._options = options_mock
        self.workflow._checkout()
        checkout_mock.assert_called()

    def test_checkout_no_environ(self):
        options_mock = mock.MagicMock(
            project='test_project', skip_checkout=False)
        self.workflow._options = options_mock
        with self.assertRaises(ExperimentException):
            self.workflow._checkout()
