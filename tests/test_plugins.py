import unittest

import scotty.workload as workload


class TestWorkloadLoading(unittest.TestCase):
    def test_load_workload_no_name(self):
        workload = workload.WorkloadLoader.load_by_path('samples/workload_gen.py')
        context = {'workload_conf': {}}
        workload.run(context)
        
    def test_load_workload_with_name(self):
        workload = workload.WorkloadLoader.load_by_path('samples/workload_gen.py', 'test_workload')
        context = {'workload_conf': {}}
        workload.run(context)
