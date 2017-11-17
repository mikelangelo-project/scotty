import unittest
import mock

from scotty.core.executor import ComponentExecutor
from scotty import utils 

class ExperimentHelperTest(unittest.TestCase):

    @mock.patch('scotty.core.context.Context')
    def test_get_workloads(self, context_mock):
        experiment = mock.Mock()
        experiment.components = {
            "workload":{ 
                "wl_1":mock.Mock(),
                "wl_2":mock.Mock()
            }
        }
        context_mock.v1._ContextV1__experiment = experiment
        experiment_helper = utils.ExperimentHelper(context_mock)
        workloads = experiment_helper.get_workloads()
        self.assertEqual(workloads, experiment.components['workload'])
