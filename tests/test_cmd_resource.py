# -*- coding: utf-8 -*-

import unittest
import argparse

from scotty.cmd.base import CommandRegistry
import scotty.cmd.resource


# TODO refactor
# TODO mock cmd.execute()
class ResourceCommandTest(unittest.TestCase):
    def test_parser(self):
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers(dest='command')
        for key in CommandRegistry.registry:
            subparser.add_parser(key)
        args = ['resource']
        command_options = parser.parse_args(args)
        command_builder = CommandRegistry.getbuilder(command_options.command)
        command_parser = CommandRegistry.getparser(command_options.command)
        command_class = CommandRegistry.getcommand_class(command_options.command)
        args = ['init']
        resource_parser = argparse.ArgumentParser()
        command_parser.add_arguments(resource_parser)
        resource_options = resource_parser.parse_args(args)
        self.assertEquals(resource_options.action, 'init')
        cmd = command_builder.buildCommand(resource_options, command_class)
        self.assertIsInstance(cmd, scotty.cmd.resource.Command)
        cmd.execute()
