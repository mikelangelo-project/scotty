import sys
import argparse

from scotty.cmd.base import CommandRegistry
import scotty.cmd.legacy


class Cli(object):

    def parse_command(self):
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers(dest='command')
        for key in CommandRegistry.registry:
            subparser.add_parser(key)
        options = parser.parse_args(sys.argv[1:2])
        self.command_builder = CommandRegistry.getbuilder(options.command)
        self.command_parser = CommandRegistry.getparser(options.command)

    def parse_command_options(self):
        parser = argparse.ArgumentParser()
        self.command_parser.add_arguments(parser)
        self.options = parser.parse_args(sys.argv[2:])

    def execute_command(self):
        cmd = self.command_builder.buildCommand(self.options)
        cmd.execute()


def run():
    cli = Cli()
    cli.parse_command()
    cli.parse_command_options()
    cli.execute_command()
