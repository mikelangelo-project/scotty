import unittest
import yaml
import sys
import imp
import os

import mock

from scotty.workflows import WorkloadRunWorkflow
from scotty.core.components import Workload
from scotty.core.context import Context
from scotty.core.workspace import WorkloadWorkspace
from scotty.core.exceptions import WorkloadException 
from scotty.cli import Cli


class WorkloadTest(unittest.TestCase):
    workload_path = 'samples/components/workload/workload_gen.py'
    workspace_path = 'samples/components/workload/'

    def setUp(self):
        self._workspace = WorkloadWorkspace(self.workspace_path)

    def _get_workload_config(self):
        workload_config = {}
        self._workspace.config_path = self.workspace_path + 'workload.yaml'
        with open(self._workspace.config_path, 'r') as stream:
            workload_config = yaml.load(stream)
        return workload_config['workload']


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


class WorkloadConfigTest(WorkloadTest):
    def test_attributes(self):
        workload_config = self._get_workload_config()
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
    def test_run(self):
        cli = Cli()
        cli.parse_command(['workload'])
        cli.parse_command_options(['run', '-c', 'samples/components/workload/workload.yaml', '-w' 'samples/components/workload'])
        workflow = WorkloadRunWorkflow(cli.options)
        workload = Workload()
        workload.workspace = self._workspace
        workflow.workload = workload
        workflow.run() 
