import sys

import scotty.utils
import scotty.cmd.legacy as cmd_legacy

COMMANDS = {
    cmd_legacy.COMMAND : cmd_legacy}

def main():
    args = scotty.utils.Args(sys.argv[1:])
    args.exec_command()

def iter_commands():
    return COMMANDS.iteritems()
