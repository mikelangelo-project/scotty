import unittest
import sys
import imp
import os

import mock

import scotty.core.workload as workload
import scotty.core.exceptions
from scotty.cli import Cli


class WorkloadTest(unittest.TestCase):
    workload_path = 'samples/workload/workload_gen.py'
    workspace_path = 'samples/workload/'

    def setUp(self):
        self._workspace = workload.Workspace(self.workspace_path)

    def _get_workload_config(self):
        workload_config = workload.WorkloadConfigLoader.load_by_path(
            self._workspace.config_path)
        return workload_config


class WorkloadModuleLoaderTest(WorkloadTest):
    def make_module(self, name, **args):
        mod = sys.modules.setdefault(name, imp.new_module(name))
        mod.__file__ = '<virtual %s>' % name
        mod.__dict__.update(**args)
        return mod

    def test_load_workload_no_name(self):
        workload_ = workload.WorkloadModuleLoader.load_by_path(self.workload_path)
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.anonymous_workload')
        self.assertEqual(workload_, module_)

    def test_load_workload_with_name(self):
        workload_ = workload.WorkloadModuleLoader.load_by_path(
            self.workload_path, 'test_workload')
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.test_workload')
        self.assertEqual(workload_, module_)

    def test_load_workspace_no_name(self):
        workload_ = workload.WorkloadModuleLoader.load_by_workspace(self._workspace)
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.anonymous_workload')
        self.assertEqual(workload_, module_)

    def test_load_workspace_with_name(self):
        workload_ = workload.WorkloadModuleLoader.load_by_workspace(
            self._workspace, 'test_workload')
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.test_workload')
        self.assertEqual(workload_, module_)


class WorkloadWorkspaceTest(WorkloadTest):
    def test_config_path(self):
        config_path = self._workspace.config_path
        config_path_expected = self.workspace_path + 'samples/workload.yaml'
        self.assertEquals(config_path, config_path_expected)

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.isfile')
    def test_fail_config_dir(self, isfile_mock, isdir_mock):
        isfile_mock.return_value = True
        isdir_mock.return_value = False
        with self.assertRaises(scotty.core.exceptions.WorkloadException):
            self._workspace.config_path

    @mock.patch('os.path.isfile')
    def test_fail_config_path(self, isfile_mock):
        isfile_mock.return_value = False
        with self.assertRaises(scotty.core.exceptions.WorkloadException):
            self._workspace.config_path

    def test_module_path(self):
        module_path = self._workspace.module_path
        self.assertEquals(module_path, 'samples/workload/workload_gen.py')

    @mock.patch('os.path.isfile')
    def test_fail_module_path(self, isfile_mock):
        isfile_mock.return_value = False
        with self.assertRaises(scotty.core.exceptions.WorkloadException):
            self._workspace.module_path

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
        workload_config = workload.WorkloadConfigLoader.load_by_path(
            self._workspace.config_path)
        self.assertEquals(workload_config['name'], 'sample_workload')
        self.assertEquals(workload_config['generator'], 'sample')
        self.assertTrue(isinstance(workload_config['params'], dict))
        self.assertTrue(isinstance(workload_config['environment'], dict))


class ContextTest(WorkloadTest):
    def test_v1_context(self):
        workload_config = self._get_workload_config()
        context = workload.Context(workload_config)
        self.assertEquals(workload_config, context.v1.workload_config)


class WorkflowTest(WorkloadTest):
    @mock.patch('git.cmd')
    def test_run_without_project(self, git_mock):
        cli = Cli()
        cli.parse_command(['workload'])
        cli.parse_command_options(['run', '-c', 'samples/workload/workload.yaml', '-w', 'samples'])
        self._test_run(cli.options)
        unpacked_calls = self._unpack_calls(git_mock.mock_calls)
        expected_calls = [('Git', ('samples/workload/',), {}),
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
        workflow = workload.Workflow(options)
        workflow.workspace = self._workspace
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
        cli.parse_command_options(['run', '-c', 'samples/workload/workload.yaml', '-w', 'samples', '-p', 'project'])
        self._test_run(cli.options)
        unpacked_calls = self._unpack_calls(git_mock.mock_calls)
        expected_calls = [('Git', ('samples/workload/',), {}),
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
        cli.parse_command_options(['run', '-c', 'samples/workload/workload.yaml', '-w', 'samples', '-p', 'project'])
        with self.assertRaises(scotty.core.exceptions.WorkloadException):
            self._test_run(cli.options, environ_dict={})

    @mock.patch('git.cmd')
    def test_with_workload_exception(self, git_mock):
        cli = Cli()
        cli.parse_command(['workload'])
        cli.parse_command_options(['run', '-c', 'samples/workload/workload.yaml', '-w', 'samples'])
        self._test_run(cli.options)
        unpacked_calls = self._unpack_calls(git_mock.mock_calls)
        expected_calls = [('Git', ('samples/workload/',), {}),
                          ('Git().clone', ('https://gerrit/p/zuul_project', '.'), {}),
                          ('Git().remote', ('update',), {}), ('Git().reset', ('--hard',), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {}),
                          ('Git().fetch', ('zuul_urlzuul_project', 'zuul_ref'), {}),
                          ('Git().checkout', ('FETCH_HEAD',), {}),
                          ('Git().reset', ('--hard', 'FETCH_HEAD'), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {})]
        self.assertEquals(unpacked_calls, expected_calls)
