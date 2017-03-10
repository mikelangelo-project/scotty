import sys
import logging

import scotty.utils
import scotty.legacy as command_legacy

COMMANDS = {
    command_legacy.COMMAND : command_legacy}

def cli():
    logging.getLogger().setLevel(logging.DEBUG)
    args = scotty.utils.Args(sys.argv[1:])
    args.exec_command()
