import sys
import argparse

from scotty.cmd.base import CommandRegistry
# The imports are not used, but are required to load the commands on startup.
import scotty.cmd.workload
import scotty.cmd.experiment
import scotty.cmd.resource


class Cli(object):
    def parse_command(self, args):
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers(dest='command')
        for key in CommandRegistry.registry:
            subparser.add_parser(key)
        options = parser.parse_args(args)
        self.command_builder = CommandRegistry.getbuilder(options.command)
        self.command_parser = CommandRegistry.getparser(options.command)
        self.command_class = CommandRegistry.getcommand_class(options.command)

    def parse_command_options(self, args):
        parser = argparse.ArgumentParser()
        self.command_parser.add_arguments(parser)
        self.options = parser.parse_args(args)

    def execute_command(self):
        cmd = self.command_builder.buildCommand(self.options,
                                                self.command_class)
        cmd.execute()


def run(args=sys.argv):
    cli = Cli()
    cli.parse_command(args[1:2])
    cli.parse_command_options(args[2:])
    cli.execute_command()
