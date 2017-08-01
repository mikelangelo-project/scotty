# -*- coding: utf-8 -*-
import argparse
import unittest

from scotty.cmd.base import CommandRegistry
from scotty.cmd.base import CommandParser


class CommandTest(object):
    def _test_parser(self):
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers(dest='command')
        for key in CommandRegistry.registry:
            subparser.add_parser(key)
        args = self.args[0:1]
        command_options = parser.parse_args(args)
        command_builder = CommandRegistry.getbuilder(command_options.command)
        command_parser = CommandRegistry.getparser(command_options.command)
        command_class = CommandRegistry.getcommand_class(command_options.command)
        args = self.args[1:]
        resource_parser = argparse.ArgumentParser()
        command_parser.add_arguments(resource_parser)
        resource_options = resource_parser.parse_args(args)
        self.assertEquals(resource_options.action, self.args[1])
        cmd = command_builder.buildCommand(resource_options, command_class)
        self.assertIsInstance(cmd, self.command_class)
        cmd.execute()


class CommandParserTest(unittest.TestCase):
    def test_parser(self):
        parser = CommandParser()
        with self.assertRaises(NotImplementedError):
            parser.add_arguments(None)
