import unittest
import sys
import os

import mock

import scotty.cli as cli
from scotty.cmd import workload
from scotty.cmd import experiment


class CliTest(object):
    def test_run(self):
        with mock.patch.object(sys, 'argv', self.args):
            environ_mock = {
                'ZUUL_PROJECT': 'zuul_project',
                'ZUUL_URL': 'zuul_url',
                'ZUUL_REF': 'zuul_ref'
            }
            with mock.patch.dict(os.environ, environ_mock):
                cli.run()


class CliWorkloadTest(CliTest, unittest.TestCase):
    args = ['./scotty.py', 'workload', 'run', '-c', 'samples/components/workload/workload.yaml', '-w', 'samples/components/workload/']

    def test_parse_workload_command(self):
        cli_ = cli.Cli()
        cli_.parse_command(self.args[1:2])
        self.assertIsInstance(cli_.command_parser, workload.CommandParser)

    def test_parse_workload_command_options(self):
        cli_ = cli.Cli()
        cli_.parse_command(self.args[1:2])
        cli_.parse_command_options(self.args[2:])
        self.assertEquals(cli_.options.action, 'run')
        self.assertFalse(cli_.options.mock)
        self.assertEquals(cli_.options.workspace, 'samples/components/workload/')


class CliExperimentTest(CliTest, unittest.TestCase):
    args = [
        './scotty.py', 'experiment', 'perform', '-w', 'samples/components/experiment'
    ]

    def test_parse_experiment_command(self):
        cli_ = cli.Cli()
        cli_.parse_command(self.args[1:2])
        self.assertIsInstance(cli_.command_parser, experiment.CommandParser)

    def test_parse_experiment_command_options(self):
        cli_ = cli.Cli()
        cli_.parse_command(self.args[1:2])
        cli_.parse_command_options(self.args[2:])
        print cli_.options
        self.assertEquals(cli_.options.action, 'perform')
        self.assertFalse(cli_.options.mock)
        self.assertEqual(cli_.options.workspace, 'samples/components/experiment')
