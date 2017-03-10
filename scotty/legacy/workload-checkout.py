#!/usr/bin/env python

import yaml
import logging
import git
import os
import sys,getopt
import glob

GERRIT_ORIGIN = "https://gerrit/p/workload_gen/"

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

def get_wl_configs(config_dir):
    return glob.glob(config_dir + "/wl_*.yaml")

def read_workload(wl_config_path):
    with open(wl_config_path, 'r') as stream:
        return yaml.load(stream)

def prepare_workload_gen(wl_configs, workspace):
    for wl_config in wl_configs:
        workload = read_workload(wl_config)
        name = workload['workload']['name']
        if 'generator' in workload['workload']:
            generator = workload['workload']['generator']
        else:
            generator = name
        logger.debug('wl-dir: %s/%s', workspace, name)
        if os.path.isdir(workspace + "/" + name):
            g = git.cmd.Git(workspace + "/" + name)
            g.pull()
        else:
            git.Git().clone(GERRIT_ORIGIN + generator, workspace + "/" + name)
        os.rename(wl_config, workspace + "/" + name + "/" + "workload.yaml")

def usage():
    print 'Usage: '+sys.argv[0]+' --config_dir=<workload_configs_folder> --workspace=<workload_generators_folder>'

def get_args(argv):
    config_dir = ""
    workspace  = ""

    opts, args = getopt.getopt(argv,"hc:w:",["help", "config_dir=", "workspace="])
    
    if not opts:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(2)
        if opt in ("-c", "--config_dir"):
            config_dir = remove_trailing_slash(arg)
        elif opt in ("-w", "--workspace"):
            workspace = remove_trailing_slash(arg)

    return config_dir, workspace

def remove_trailing_slash(path):
  return path.rstrip('/')

def main():
    """The main program."""
    global logger
    logger = get_logger()

    config_dir, workspace = get_args(sys.argv[1:])
    wl_configs            = get_wl_configs(config_dir)

    logger.debug('config_dir: %s', config_dir)
    logger.debug('workspace: %s' , workspace)
    logger.debug('wl_configs: %s', wl_configs)

    prepare_workload_gen(wl_configs, workspace)

if __name__ == '__main__':
    main()
