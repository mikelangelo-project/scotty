#!/usr/bin/env python

import logging
import os
import sys,getopt
import subprocess

def get_logger():
    """Setup the global logger."""
    
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    logger.addHandler(ch)
    logger.debug('Logger setup complete. Start Program ... ')
    return logger

def usage():
    print 'Usage: '+sys.argv[0]+' --workspace=<workload_generators> --multiple'

def get_args(argv):
    workspace = ""
    multiple  = False

    opts, args = getopt.getopt(argv,"hw:m",["help", "workspace=", "multiple"])
    
    if not opts:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        elif opt in ("-w", "--workspace"):
            workspace = remove_trailing_slash(arg)
        elif opt in ("-m", "--multiple"):
            multiple = True

    return workspace, multiple

def get_workload_dirs(workspace):
    return [os.path.join(workspace, subdir) for subdir in os.listdir(workspace) if os.path.isdir(os.path.join(workspace, subdir))]

def run(workspace, multiple = False):
    if multiple:
        #loop all in workspace and execute run(workspace_wl)
        logger.debug('Run multiple workloads in: %s', workspace)
        
        for wl_gen in get_workload_dirs(workspace):
            run(wl_gen)
    else:
        data_dir = os.getcwd()
        logger.info('Run workload: %s', workspace)
        logger.info('Run workload with datadir %s', data_dir)
        subprocess.check_call(['./run.py', '-w', './workload.yaml', '-d', data_dir], cwd=workspace + '/')


def remove_trailing_slash(path):
  return path.rstrip('/')

def main():
    """The main program."""
    global logger
    logger = get_logger()

    workspace, multiple = get_args(sys.argv[1:])

    run(workspace, multiple)

if __name__ == '__main__':
    main()
