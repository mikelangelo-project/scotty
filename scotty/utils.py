import argparse
import logging

import scotty

class Args:
    def __init__(self, args):
        self.__setup()
        self.__args = self.__parser.parse_args(args)

    def __setup(self):
        self.__parser = argparse.ArgumentParser()
        for command in scotty.COMMANDS:
            scotty.COMMANDS[command].setup_parser(self.__parser)
            
    def getargs(self):
        return self.__args

    def exec_command(self):
        scotty.COMMANDS[self.__args.command].run(self)
