import unittest
import mock

from concurrent.futures import wait as futures_wait

from scotty.core.executor import ComponentExecutor
from scotty.core.executor import WorkloadRunExecutor
from scotty.core.executor import ResourceDeployExecutor
from scotty.core.exceptions import ScottyException

class ComponentExecutorTest(unittest.TestCase):
    @mock.patch('scotty.core.executor.ComponentExecutor._exec_with_context')
    def test_submit_execute(self, _exec_with_context_mock):
        component_executor = ComponentExecutor()
        component_executor.submit('experiment', 'component', 'interface_')
        futures_wait(component_executor._future_to_component)
        _exec_with_context_mock.assert_called()

    @mock.patch('scotty.core.context.Context')
    @mock.patch('scotty.core.executor.ComponentExecutor._get_function')
    @mock.patch('scotty.core.executor.ComponentExecutor._exec_function')
    @mock.patch('scotty.core.components.Experiment')
    @mock.patch('scotty.core.components.Component')
    def test__exec_with_context(self, component_mock, experiment_mock, _exec_function_mock, _get_function_mock, context_mock):
        component_executor = ComponentExecutor()
        component_executor._exec_with_context(experiment_mock, component_mock, 'run')
        _exec_function_mock.assert_called()

    def test__get_function(self):#, getattr_mock):
        pass

    @mock.patch('scotty.core.components.Component')
    @mock.patch('scotty.core.context.Context')
    def test__exec_function(self, context_mock, component_mock):
        function__mock = mock.Mock(return_value='return_value')
        component_executor = ComponentExecutor()
        return_value = component_executor._exec_function(component_mock, function__mock, context_mock)
        self.assertEqual(return_value, function__mock.return_value)
        
    @mock.patch('scotty.core.components.Component')
    @mock.patch('scotty.core.context.Context')
    @mock.patch('scotty.core.executor.ComponentExecutor._log_component_exception')
    def test__exec_function_exception(self, _log_component_exception_mock, context_mock, component_mock):
        function__mock = mock.Mock(side_effect=Exception())
        component_executor = ComponentExecutor()
        component_executor._exec_function(component_mock, function__mock, context_mock)
        _log_component_exception_mock.assert_called()

    @mock.patch('scotty.core.executor.logger.exception')
    @mock.patch('scotty.core.components.Component')
    def test__log_component_exception(self, component_mock, logger_exception_mock):
        component_executor = ComponentExecutor()
        component_executor._log_component_exception(component_mock)
        logger_exception_mock.assert_called()

class WorkloadExecutorTest(unittest.TestCase):
    @mock.patch('scotty.core.executor.ComponentExecutor.submit')
    @mock.patch('scotty.core.components.Experiment')
    def test_submit_workloads(self, experiment_mock, submit_mock):
        workloads_mock = {}
        workloads_mock['workload_1'] = mock.Mock()
        workloads_mock['workload_2'] = mock.Mock()
        experiment_mock.components = {}
        experiment_mock.components['workload'] = workloads_mock
        workload_run_executor = WorkloadRunExecutor()
        workload_run_executor.submit_workloads(experiment_mock)
        submit_mock.assert_called()

    def test_collect_results(self):
        pass


class ResourceDeployExecutorTest(unittest.TestCase):
    @mock.patch('scotty.core.executor.ComponentExecutor.submit')
    @mock.patch('scotty.core.components.Experiment')
    def test_submit_resources(self, experiment_mock, submit_mock):
        resources_mock = {}
        resources_mock['resource_1'] = mock.Mock()
        resources_mock['resource_2'] = mock.Mock()
        experiment_mock.components = {}
        experiment_mock.components['resource'] = resources_mock
        resource_deploy_executor = ResourceDeployExecutor()
        resource_deploy_executor.submit_resources(experiment_mock)
        submit_mock.assert_called()
