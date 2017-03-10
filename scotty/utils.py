import argparse
import logging

import scotty.legacy as command_legacy

class Args:
    def __init__(self, args):
        self.__setup()
        self.__args = self.__parser.parse_args(args)

    def __setup(self):
        self.__parser = argparse.ArgumentParser()
        self.__commands = {
            command_legacy.COMMAND : command_legacy}
        for command in self.__commands:
            self.__commands[command].setup_parser(self.__parser)
            
    def getargs(self):
        return self.__args

    def exec_command(self):
        self.__commands[self.__args.command].run(self)
