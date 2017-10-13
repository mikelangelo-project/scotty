import unittest
import os
import contextlib

from scotty import cli 


class PerformExperimentTest(unittest.TestCase):
    args = [
        'experiment', 'perform'
    ]

    experiment_path = 'samples/components/experiment/'
        
    @contextlib.contextmanager
    def cwd(self, path):
        prev_cwd = os.getcwd()
        os.chdir(path)
        yield
        os.chdir(prev_cwd)

    def test_perform_experiment(self):
        with self.cwd(self.experiment_path):
            cli_ = cli.Cli()
            cli_.parse_command(self.args[0:1])
        
