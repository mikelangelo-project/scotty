import sys
import logging

import scotty.utils

def cli():
    logging.getLogger().setLevel(logging.DEBUG)
    args = scotty.utils.Args(sys.argv[1:])
    args.exec_command()
