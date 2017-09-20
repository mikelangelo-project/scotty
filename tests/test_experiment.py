import unittest
import os

import mock

from scotty.core.components import Experiment
from scotty.core.components import Workload
from scotty.core.workspace import ExperimentWorkspace
from scotty.workflows import ExperimentPerformWorkflow
from scotty.core.exceptions import ExperimentException


def mock_workspace(workspace_path='samples/components/experiment'):
    return ExperimentWorkspace(workspace_path)


class ExperimentWorkspaceTest(unittest.TestCase):
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
        sample_path = os.path.abspath('samples/components/experiment/experiment.yaml')
        self.assertEquals(config_path, sample_path)

    def test_cwd(self):
        workspace = mock_workspace()
        with workspace.cwd():
            wd = os.getcwd()
        cwd = os.getcwd()
        wd_should = os.path.join(cwd, 'samples/components/experiment')
        self.assertEquals(wd, wd_should)


class ExperimentTest(unittest.TestCase):
    def test_add_workload(self):
        experiment = Experiment()
        workload = Workload()
        workload.config = {'name': 'test_name'}
        experiment.add_component(workload)
        self.assertEquals(experiment.workloads['test_name'], workload)
        self.assertEquals(len(experiment.workloads), 1)

    def test_add_experiment(self):
        parent_experiment = Experiment()
        child_experiment = Experiment()
        with self.assertRaises(ExperimentException):
            parent_experiment.add_component(child_experiment)


class ExperimentWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.workflow = ExperimentPerformWorkflow(options=None)

    @mock.patch('scotty.workflows.ExperimentPerformWorkflow._prepare')
    @mock.patch('scotty.workflows.ExperimentPerformWorkflow._load')
    @mock.patch('scotty.workflows.ExperimentPerformWorkflow._run')
    @mock.patch('scotty.workflows.ExperimentPerformWorkflow._clean')
    def test_run(self, prepare_mock, load_mock, run_mock, clean_mock):
        self.workflow.run()
        prepare_mock.assert_called()
        load_mock.assert_called()
        run_mock.assert_called()
        clean_mock.assert_called()

    def test_prepare(self):
        options_mock = mock.MagicMock(workspace='.')
        self.workflow._options = options_mock
        self.workflow._prepare()
        new_workspace = self.workflow.experiment.workspace
        workspace_path = new_workspace.path
        cwd = os.getcwd()
        self.assertEquals(workspace_path, cwd)
