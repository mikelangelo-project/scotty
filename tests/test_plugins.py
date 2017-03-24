import unittest

import scotty.plugins as plugins


class TestWorkloadLoading(unittest.TestCase):
    def test_load_workload_no_name(self):
        workload = plugins.WorkloadLoader.load_by_path('samples/workload_gen_dummy.py', {})
        context = {'workload_conf': {}}
        workload.run(context)
