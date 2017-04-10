import unittest
import logging
import sys
import imp

import scotty.workload as workload


class TestWorkloadLoading(unittest.TestCase):
    def make_module(self, name, **args):
        mod = sys.modules.setdefault(name, imp.new_module(name))
        mod.__file__ = '<virtual %s>' % name
        mod.__dict__.update(**args)
        return mod

    def test_load_workload_no_name(self):
        workload_ = workload.WorkloadLoader.load_by_path('samples/workload/workload_gen.py')
        module_ = self.make_module('scotty.workload-gen.anonymous_workload')
        self.assertEqual(workload_, module_)
        print('Workload loaded with no names: OK')
        
    def test_load_workload_with_name(self):
        workload_ = workload.WorkloadLoader.load_by_path('samples/workload/workload_gen.py', 'test_workload')
        module_ = self.make_module('scotty.workload-gen.test_workload')
        self.assertEqual(workload_, module_)
        print('Workload loaded with name: OK')
