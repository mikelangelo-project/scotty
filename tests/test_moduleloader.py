import unittest
import sys
import imp

from scotty.core.moduleloader import ModuleLoader

class ModuleLoaderTest(unittest.TestCase):
    workload_path = 'samples/components/experiment/workload/demo/workload_gen.py'

    def make_module(self, name, **args):
        mod = sys.modules.setdefault(name, imp.new_module(name))
        mod.__file__ = '<virtual %s>' % name
        mod.__dict__.update(**args)
        return mod

    def test_load_module_with_name(self):
        workload_ = ModuleLoader.load_by_path(
            self.workload_path, 
            'test_workload', 
            'scotty.workload_gen')
        self.assertTrue('run' in dir(workload_))
        module_ = self.make_module('scotty.workload_gen.test_workload')
        self.assertEqual(workload_, module_)
