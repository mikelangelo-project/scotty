import unittest
import sys
import imp
import os

import mock

from scotty.core.workload import Workload, WorkloadConfigLoader, Workflow
from scotty.core.context import Context
from scotty.core.workspace import Workspace
import scotty.core.exceptions
from scotty.cli import Cli


class WorkloadTest(unittest.TestCase):
    workload_path = 'samples/components/workload/workload_gen.py'
    workspace_path = 'samples/components/workload/'

    def setUp(self):
        self._workspace = Workspace(self.workspace_path)

    def _get_workload_config(self):
        workload_config = WorkloadConfigLoader.load_by_path(
            self.workspace_path + 'workload.yaml')
        return workload_config


class WorkloadWorkspaceTest(WorkloadTest):
    def test_module_path(self):
        workload = Workload()
        workload.workspace = self._workspace 
        module_path = workload.module_path
        self.assertEquals(module_path, os.path.abspath('samples/components/workload/workload_gen.py'))

    def test_cwd(self):
        with self._workspace.cwd():
            wd = os.getcwd()
        workspace_path = os.path.abspath(self.workspace_path)
        self.assertEquals(wd, workspace_path)


class WorkloadConfigLoaderTest(WorkloadTest):
    def test_load_by_workspace(self):
        workload_config = self._get_workload_config()
        self.assertIsNotNone(workload_config)


class WorkloadConfigTest(WorkloadTest):
    def test_attributes(self):
        workload_config = WorkloadConfigLoader.load_by_path(
            self.workspace_path + 'workload.yaml')
        self.assertEquals(workload_config['name'], 'sample_workload')
        self.assertEquals(workload_config['generator'], 'sample')
        self.assertTrue(isinstance(workload_config['params'], dict))
        self.assertTrue(isinstance(workload_config['environment'], dict))


class ContextTest(WorkloadTest):
    def test_v1_context(self):
        workload_config = self._get_workload_config()
        context = Context(workload_config)
        self.assertEquals(workload_config, context.v1.workload_config)


class WorkflowTest(WorkloadTest):
    @mock.patch('git.cmd')
    def test_run_without_project(self, git_mock):
        cli = Cli()
        cli.parse_command(['workload'])
        cli.parse_command_options(['run', '-c', 'samples/components/workload/workload.yaml', '-w', 'samples/components/workload'])
        self._test_run(cli.options)
        unpacked_calls = self._unpack_calls(git_mock.mock_calls)
        expected_calls = [('Git', (os.path.abspath('samples/components/workload/'),), {}),
                          ('Git().clone', ('https://gerrit/p/zuul_project', '.'), {}),
                          ('Git().remote', ('update',), {}),
                          ('Git().reset', ('--hard',), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {}),
                          ('Git().fetch', ('zuul_urlzuul_project', 'zuul_ref'), {}),
                          ('Git().checkout', ('FETCH_HEAD',), {}),
                          ('Git().reset', ('--hard', 'FETCH_HEAD'), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {})]
        self.assertEquals(unpacked_calls, expected_calls)

    def _unpack_calls(self, mock_calls):
        unpacked_calls = []
        for mock_call in mock_calls:
            name, args, kwargs = mock_call
            unpacked_calls.append((name, args, kwargs))
        return unpacked_calls

    def _test_run(self, options, environ_dict=None):
        workflow = Workflow(options)
        workload = Workload()
        workload.workspace = self._workspace
        workflow.workload = workload
        if environ_dict is None:
            environ_dict = {
                'ZUUL_PROJECT': 'zuul_project',
                'ZUUL_URL': 'zuul_url',
                'ZUUL_REF': 'zuul_ref'
            }
        with mock.patch.dict(os.environ, environ_dict):
            workflow.run()

    @mock.patch('git.cmd')
    def test_run_with_project(self, git_mock):
        cli = Cli()
        cli.parse_command(['workload'])
        cli.parse_command_options(['run', '-c', 'samples/components/workload/workload.yaml', '-w', 'samples/components/workload', '-p', 'project'])
        self._test_run(cli.options)
        unpacked_calls = self._unpack_calls(git_mock.mock_calls)
        expected_calls = [('Git', (os.path.abspath('samples/components/workload/'),), {}),
                          ('Git().clone', ('https://gerrit/p/project', '.'), {}),
                          ('Git().remote', ('update',), {}),
                          ('Git().reset', ('--hard',), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {}),
                          ('Git().fetch', ('zuul_urlproject', 'zuul_ref'), {}),
                          ('Git().checkout', ('FETCH_HEAD',), {}),
                          ('Git().reset', ('--hard', 'FETCH_HEAD'), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {})]
        self.assertEquals(unpacked_calls, expected_calls)

    def test_without_zuul_settings(self):
        cli = Cli()
        cli.parse_command(['workload'])
        cli.parse_command_options(['run', '-c', 'samples/components/workload/workload.yaml', '-w', 'samples/components/workload', '-p', 'project'])
        with self.assertRaises(scotty.core.exceptions.WorkloadException):
            self._test_run(cli.options, environ_dict={})

    @mock.patch('git.cmd')
    def test_with_workload_exception(self, git_mock):
        cli = Cli()
        cli.parse_command(['workload'])
        cli.parse_command_options(['run', '-c', 'samples/components/workload/workload.yaml', '-w', 'samples/components/workload'])
        self._test_run(cli.options)
        unpacked_calls = self._unpack_calls(git_mock.mock_calls)
        expected_calls = [('Git', (os.path.abspath('samples/components/workload/'),), {}),
                          ('Git().clone', ('https://gerrit/p/zuul_project', '.'), {}),
                          ('Git().remote', ('update',), {}), ('Git().reset', ('--hard',), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {}),
                          ('Git().fetch', ('zuul_urlzuul_project', 'zuul_ref'), {}),
                          ('Git().checkout', ('FETCH_HEAD',), {}),
                          ('Git().reset', ('--hard', 'FETCH_HEAD'), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {})]
        self.assertEquals(unpacked_calls, expected_calls)
