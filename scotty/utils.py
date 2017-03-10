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
            command.setup_parser(self._parser)
            
    def getargs(self):
        return self._args

    def exec_command(self):
        scotty.cli.COMMANDS[self._args.command].main(self)
