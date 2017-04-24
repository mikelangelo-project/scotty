import unittest
import sys
import os

import mock

import scotty.cli as cli
from scotty.cmd.workload import CommandBuilder
from scotty.cmd.workload import CommandParser


class CliTest(unittest.TestCase):
    args = ['./scotty.py', 'workload', 'run', '-w', 'samples/workload/', '-s']

    def test_parse_command(self):
        cli_ = cli.Cli()
        cli_.parse_command(self.args[1:2])
        self.assertIsInstance(cli_.command_builder, CommandBuilder)
        self.assertIsInstance(cli_.command_parser, CommandParser)

    def test_parse_command_options(self):
        cli_ = cli.Cli()
        cli_.parse_command(self.args[1:2])
        cli_.parse_command_options(self.args[2:])
        self.assertEquals(cli_.options.action, 'run')
        self.assertFalse(cli_.options.mock)
        self.assertIsNone(cli_.options.project)
        self.assertEquals(cli_.options.workspace, 'samples/workload/')
        self.assertTrue(cli_.options.skip_checkout)

    def test_run(self):
        with mock.patch.object(sys, 'argv', self.args):
            environ_mock = {
                'ZUUL_PROJECT': 'zuul_project',
                'ZUUL_URL': 'zuul_url',
                'ZUUL_REF': 'zuul_ref'
            }
            with mock.patch.dict(os.environ, environ_mock):
                cli.run()
