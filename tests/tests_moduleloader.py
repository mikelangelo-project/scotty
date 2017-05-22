import unittest
import sys
import imp

from scotty.core.moduleloader import ModuleLoader


class WorkloadModuleLoaderTest(unittest.TestCase):
    workload_path = 'samples/components/workload/workload_gen.py'

    def setUp(self):
        self._module_loader = ModuleLoader('scotty.workload_gen', 'anonymous_workload')

    def make_module(self, name, **args):
        mod = sys.modules.setdefault(name, imp.new_module(name))
        mod.__file__ = '<virtual %s>' % name
        mod.__dict__.update(**args)
        return mod

    def test_load_workload_no_name(self):
        workload_ = self._module_loader.load_by_path(self.workload_path)
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.anonymous_workload')
        self.assertEqual(workload_, module_)

    def test_load_workload_with_name(self):
        workload_ = self._module_loader.load_by_path(self.workload_path, 'test_workload')
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.test_workload')
        self.assertEqual(workload_, module_)
