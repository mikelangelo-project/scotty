import unittest
import errno
import os
import contextlib
import shutil

from scotty import cli


class CleanExperimentTest(unittest.TestCase):
    cli_cmd = 'scotty experiment clean'
    test_script_name = os.path.basename(__file__)
    test_script_name = os.path.splitext(test_script_name)[0]
    experiment_samples_path = 'samples/components/experiment/single_workload'
    experiment_tmp_path_root = os.path.join('tmp', test_script_name)
    experiment_tmp_path = os.path.join(experiment_tmp_path_root, experiment_samples_path)
    experiment_scotty_path = os.path.join(experiment_tmp_path, '.scotty')

    def setUp(self):
        if os.path.isdir(self.experiment_tmp_path):
            shutil.rmtree(self.experiment_tmp_path)
        shutil.copytree(self.experiment_samples_path, self.experiment_tmp_path)
        self.create_scotty_dir()

    def create_scotty_dir(self):
        try:
            os.makedirs(self.experiment_scotty_path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(self.experiment_scotty_path):
                pass
            else:
                raise

    def tearDown(self):
        shutil.rmtree(self.experiment_tmp_path_root)

    def test_clean_experiment(self):
        self.run_cmd()
        self.assertFalse(os.path.exists(self.experiment_scotty_path))

    @contextlib.contextmanager
    def cwd(self, path):
       prev_cwd = os.getcwd()
       os.chdir(path)
       try:
           yield
       finally:
           os.chdir(prev_cwd)

    def run_cmd(self):
         with self.cwd(self.experiment_tmp_path):
             cmd_args = self.cli_cmd.split(' ')
             cli.run(cmd_args)
