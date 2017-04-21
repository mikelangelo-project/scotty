import unittest
import sys
import imp
import os

import mock

import scotty.workload as workload
from scotty.cli import Cli


class WorkloadTest(unittest.TestCase):
    workload_path = 'samples/workload/workload_gen.py'
    workspace_path = 'samples/workload/'

    def setUp(self):
        self._workspace = workload.WorkloadWorkspace(
            self.workspace_path, git_=workload.GitMock)

    def _get_workload_config(self):
        workload_config = workload.WorkloadConfigLoader.load_by_workspace(
            self._workspace)
        return workload_config


class WorkloadLoaderTest(WorkloadTest):
    def make_module(self, name, **args):
        mod = sys.modules.setdefault(name, imp.new_module(name))
        mod.__file__ = '<virtual %s>' % name
        mod.__dict__.update(**args)
        return mod

    def test_load_workload_no_name(self):
        workload_ = workload.WorkloadLoader.load_by_path(self.workload_path)
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.anonymous_workload')
        self.assertEqual(workload_, module_)

    def test_load_workload_with_name(self):
        workload_ = workload.WorkloadLoader.load_by_path(
            self.workload_path, 'test_workload')
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.test_workload')
        self.assertEqual(workload_, module_)

    def test_load_workspace_no_name(self):
        workload_ = workload.WorkloadLoader.load_by_workspace(self._workspace)
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.anonymous_workload')
        self.assertEqual(workload_, module_)

    def test_load_workspace_with_name(self):
        workload_ = workload.WorkloadLoader.load_by_workspace(
            self._workspace, 'test_workload')
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.test_workload')
        self.assertEqual(workload_, module_)


class WorkloadWorkspaceTest(WorkloadTest):
    def test_config_path(self):
        config_path = self._workspace.config_path
        config_path_expected = self.workspace_path + 'samples/workload.yaml'
        self.assertEquals(config_path, config_path_expected)

    def test_workload_path(self):
        workload_path = self._workspace.workload_path
        self.assertEquals(workload_path, 'samples/workload/workload_gen.py')

    def test_cwd(self):
        with self._workspace.cwd():
            wd = os.getcwd()
        workspace_path = os.path.abspath(self.workspace_path)
        self.assertEquals(wd, workspace_path)

    def test_checkout(self):
        self._workspace.checkout(
            project='project',
            gerrit_url='gerrit_url',
            zuul_url='zuul_url',
            zuul_ref='zuul_ref')
        action_log = self._workspace._git_repo.action_log
        action_log_expected = [
            "clone ('gerrit_urlproject', '.')", "remote ('update',)",
            "reset (('--hard',),)", "clean (('-x', '-f', '-d', '-q'),)",
            "fetch ('zuul_urlproject', 'zuul_ref')",
            "checkout ('FETCH_HEAD',)", "reset (('--hard', 'FETCH_HEAD'),)",
            "clean (('-x', '-f', '-d', '-q'),)"
        ]
        self.assertEquals(action_log, action_log_expected)


class WorkloadConfigLoaderTest(WorkloadTest):
    def test_load_by_workspace(self):
        workload_config = self._get_workload_config()
        self.assertIsNotNone(workload_config)


class WorkloadConfigTest(WorkloadTest):
    def test_attributes(self):
        workload_config = workload.WorkloadConfigLoader.load_by_workspace(
            self._workspace)
        self.assertEquals(workload_config.name, 'sample_workload')
        self.assertEquals(workload_config.generator, 'sample')
        self.assertTrue(isinstance(workload_config.params, dict))
        self.assertTrue(isinstance(workload_config.environment, dict))


class ContextTest(WorkloadTest):
    def test_v1_context(self):
        workload_config = self._get_workload_config()
        context = workload.Context(workload_config)
        self.assertEquals(workload_config, context.v1.workload_config)


class WorkflowTest(WorkloadTest):
    def test_run(self):
        cli = Cli()
        cli.parse_command(['workload'])
        cli.parse_command_options(['run', '-w', 'samples'])
        options = cli.options
        workflow = workload.Workflow(options)
        workflow.workspace = self._workspace
        environ_dict = {
            'ZUUL_PROJECT': 'zuul_project',
            'ZUUL_URL': 'zuul_url',
            'ZUUL_REF': 'zuul_ref'
        }
        with mock.patch.dict(os.environ, environ_dict):
            workflow.run()
        git_action_log = workflow.workspace._git_repo.action_log
        git_actions_expected = [
            "clone ('https://gerrit/p/zuul_project', '.')",
            "remote ('update',)", "reset (('--hard',),)",
            "clean (('-x', '-f', '-d', '-q'),)",
            "fetch ('zuul_urlzuul_project', 'zuul_ref')",
            "checkout ('FETCH_HEAD',)", "reset (('--hard', 'FETCH_HEAD'),)",
            "clean (('-x', '-f', '-d', '-q'),)"
        ]
        self.assertEqual(git_action_log, git_actions_expected)
