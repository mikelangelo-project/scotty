import unittest
import mock
import uuid

from scotty.core.executor import ComponentExecutor
from scotty.core.components import Experiment
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

    @mock.patch('scotty.core.context.Context')
    def test_get_experiment_uuid(self, context_mock):
        experiment = Experiment()
        context_mock.v1._ContextV1__experiment = experiment
        experiment_helper = utils.ExperimentHelper(context_mock)
        uuid = experiment_helper.get_experiment_uuid()
        uuid_string = str(uuid)
        self.assertTrue(self.validate_uuid4(uuid_string))

    def validate_uuid4(self, uuid_string):
        try:
            val = uuid.UUID(uuid_string, version=4)
        except ValueError:
            return False
        return True
