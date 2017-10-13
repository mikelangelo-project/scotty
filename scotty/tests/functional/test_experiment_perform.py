import unittest
import os
import contextlib
import shutil

from scotty import cli


class PerformExperimentTest(unittest.TestCase):
    cli_cmd = 'scotty experiment perform'
    experiment_samples_path = 'samples/components/experiment/single_workload'
    experiment_tmp_path = os.path.join('tmp', experiment_samples_path)

    def setUp(self):
        if os.path.isdir(self.experiment_tmp_path):
            shutil.rmtree(self.experiment_tmp_path)
        shutil.copytree(self.experiment_samples_path, self.experiment_tmp_path)

    def tearDown(self):
        pass
        #shutil.rmtree(self.experiment_tmp_path)

    def test_perform_experiment(self):
        self.run_cmd()
        experiment_scotty_path = os.path.join(self.experiment_tmp_path, '.scotty/')
        workload_module_path = os.path.join(
            experiment_scotty_path, 
            'components/workloads/demo_workload/workload_gen.py')
        resource_module_path = os.path.join(
            experiment_scotty_path,
            'components/resources/demo_resource/resource_gen.py')
        self.assertTrue(os.path.isdir(experiment_scotty_path), 'Missing .scotty directory')
        self.assertTrue(os.path.exists(workload_module_path), 'Missing module for demo_workload')
        self.assertTrue(os.path.exists(resource_module_path), 'Missing module for demo_resource')
        #check resource result
        #check workload result 

    @contextlib.contextmanager
    def cwd(self, path):
        prev_cwd = os.getcwd()
        os.chdir(path)
        yield
        os.chdir(prev_cwd)

    def run_cmd(self):
        with self.cwd(self.experiment_tmp_path):
            cmd_args = self.cli_cmd.split(' ')
            cli.run(cmd_args)
