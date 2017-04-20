import unittest
import sys
import imp

import scotty.workload as workload


class TestWorkloadLoading(unittest.TestCase):
    workload_path = 'samples/workload/workload_gen.py'
    workspace_path = 'samples/workload/'

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
        workspace = workload.WorkloadWorkspace(self.workspace_path)
        workload_ = workload.WorkloadLoader.load_by_workspace(workspace)
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.anonymous_workload')
        self.assertEqual(workload_, module_)

    def test_load_workspace_with_name(self):
        workspace = workload.WorkloadWorkspace(self.workspace_path)
        workload_ = workload.WorkloadLoader.load_by_workspace(
            workspace, 'test_workload')
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.test_workload')
        self.assertEqual(workload_, module_)
