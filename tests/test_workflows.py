import unittest
import mock

from scotty.workflows import Workflow, ExperimentPerformWorkflow
from scotty.core.exceptions import ScottyException, ResourceException, WorkloadException
from scotty.core.context import Context


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        self._workflow = Workflow(None)

    def test_workflow_prepare(self):
        with self.assertRaises(NotImplementedError):
            self._workflow._prepare()

    def test_workflow_load(self):
        with self.assertRaises(NotImplementedError):
            self._workflow._load()

    def test_workflow_run(self):
        with self.assertRaises(NotImplementedError):
            self._workflow._run()

    def test_workflow_clean(self):
        self._workflow._clean()


class ExperimentPerformWorkflowTest(unittest.TestCase):
    class Options(object):
        config = 'mocked_config'
        mock = False

    class ComponentMock(object):
        name = 'test_component'

    def setUp(self):
        self._workflow = ExperimentPerformWorkflow(None)

    def test_load_with_config(self):
        self._workflow._options = self.Options()
        self._workflow._load_config = mock.MagicMock()
        self._workflow.experiment = mock.MagicMock()
        self._workflow._load()

    def test_run(self):
        self._workflow._options = self.Options()
        self._workflow._check_components = mock.MagicMock()
        self._workflow._deploy_resources = mock.MagicMock()
        self._workflow._deploy_resources.side_effect = Exception('Boom!')
        self._workflow._run()

    def test_check_components_fail_resource(self):
        workflow = self._workflow
        workflow.experiment = mock.MagicMock()
        resource_mock = self.ComponentMock()
        workflow.experiment.resources = {'foo': resource_mock}
        with self.assertRaises(ScottyException):
            workflow._check_components()

    def test_check_components_fail_workload(self):
        workflow = self._workflow
        workflow.experiment = mock.MagicMock()
        workload = self.ComponentMock()
        workflow.experiment.workloads = {'test_workload': workload}
        with self.assertRaises(ScottyException):
            workflow._check_components()

    @mock.patch.object(Context, '__init__', lambda x, y, z: None)
    def test_deploy_resource(self):
        workflow = self._workflow
        workflow.experiment = mock.MagicMock()
        resource = self.ComponentMock()
        workflow.experiment.resources = {'test_resource': resource}
        with self.assertRaises(ResourceException):
            workflow._deploy_resources()

    @mock.patch.object(Context, '__init__', lambda x, y, z: None)
    def test_deploy_workload(self):
        workflow = self._workflow
        workflow.experiment = mock.MagicMock()
        workload = self.ComponentMock()
        workflow.experiment.workloads = {'test_workload': workload}
        with self.assertRaises(WorkloadException):
            workflow._run_workloads()

    @mock.patch.object(Context, '__init__', lambda x, y, z: None)
    def test_clean_resources(self):
        workflow = self._workflow
        workflow.experiment = mock.MagicMock()
        resource = self.ComponentMock()
        workflow.experiment.resources = {'test_resource': resource}
        with self.assertRaises(ResourceException):
            workflow._clean_resources()
