import argparse
import logging

import scotty

class Args(object):
    def __init__(self, args):
        self._setup()
        self._args = self._parser.parse_args(args)

    def _setup(self):
        self._parser = argparse.ArgumentParser()
        for key, command in scotty.cli.iter_commands():
	    self._setup_command(command)
     
    def _setup_command(self, command):
        subparser = self._parser.add_subparsers(
	    help = command.HELP,
            dest = 'command')
        cmd_parser = subparser.add_parser(command.COMMAND)
        command.setup_parser(cmd_parser)
            
    def getargs(self):
        return self._args

    def exec_command(self):
        scotty.cli.COMMANDS[self._args.command].main(self)
