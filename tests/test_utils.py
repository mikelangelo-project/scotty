import unittest

from scotty.utils import ExperimentHelper
from scotty.core.context import Context
from scotty.core.components import Experiment, Workload, Resource
from scotty.core.exceptions import ScottyException


class TestExperimentHelper(unittest.TestCase):
    def setUp(self):
        resource = Resource()
        resource.config = {'name': 'test_resource'}
        experiment = Experiment()
        experiment.add_component(resource)
        workload = Workload()
        context = Context(workload, experiment)
        self._experiment_helper = ExperimentHelper(context)

    def test_open_abs_file(self):
        abs_path = '/tmp'
        with self.assertRaises(ScottyException):
            with self._experiment_helper.open_file(abs_path):
                pass

    def test_open_rel_file(self):
        readme_path = 'README.md'
        with self._experiment_helper.open_file(readme_path) as file_:
            contents = file_.read()
            self.assertGreater(len(contents), 0)

    def test_fail_get_resource(self):
        with self.assertRaises(ScottyException):
            self._experiment_helper.get_resource('foo')

    def test_get_resource(self):
        self._experiment_helper.get_resource('test_resource')
