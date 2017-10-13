import unittest
import os
import contextlib
import shutil

from scotty import cli 


class PerformExperimentTest(unittest.TestCase):
    args = [
        'experiment', 'perform'
    ]

    experiment_samples_path = 'samples/components/experiment/single_workload'
    experiment_tmp_path = os.path.join('tmp', experiment_samples_path)

    def setUp(self):
        shutil.copytree(self.experiment_samples_path, self.experiment_tmp_path)
        pass #copy samples to tmp

    def tearDown(self):
        pass #delete samples from tmp

    def test_perform_experiment(self):
        with self.cwd(self.experiment_tmp_path):
            cli_ = cli.Cli()
            cli_.parse_command(self.args[0:1])
        #schauen ob .scotty verzeichniss geschrieben wurde
        #schauen ob resource ergebniss richtig geschrieben
        #schauen ob workload ergebnisse richtig geschrieben hat 

    @contextlib.contextmanager
    def cwd(self, path):
        prev_cwd = os.getcwd()
        os.chdir(path)
        yield
        os.chdir(prev_cwd)
