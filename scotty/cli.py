import sys
import logging

import scotty.utils
import scotty.cmd.legacy as cmd_legacy

COMMANDS = {
    cmd_legacy.COMMAND : cmd_legacy}

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    args = scotty.utils.Args(sys.argv[1:])
    args.exec_command()

def iter_commands():
    return COMMANDS.iteritems()
