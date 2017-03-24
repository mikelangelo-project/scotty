import sys
import argparse
import logging

from scotty.cmd.base import CommandRegistry
import scotty.cmd.legacy

def run():
    cmd_builder, cmd_parser = parse_command()
    parser = argparse.ArgumentParser()
    cmd_parser.add_arguments(parser)
    options = parser.parse_args(sys.argv[2:])
    cmd = cmd_builder.buildCommand(options)
    cmd.execute()

def parse_command():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest = 'command')
    for key in CommandRegistry.registry:
        subparser.add_parser(key)
    options = parser.parse_args(sys.argv[1:2])
    return (CommandRegistry.getbuilder(options.command),
            CommandRegistry.getparser(options.command))
