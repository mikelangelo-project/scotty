#!/usr/bin/env python

import yaml
import sys,getopt
import os
  

def split_experiment(experiment, wl_configs):
  touch_dir(wl_configs)
  try:
    workloads = read_experiment(experiment)
    for workload in workloads:
      dest_path = wl_configs + "/" + "wl_" + workload['workload']['name'] + '.yaml'
      write_workload(dest_path, workload)
  except yaml.YAMLError as out:
    print(out)

def touch_dir(wl_configs):
  if not os.path.isdir(wl_configs):
    os.mkdir(wl_configs)

def read_experiment(experiment_path):
  with open(experiment_path, "r") as stream:
    return yaml.load(stream)

def write_workload(dest_path, workload):
  with open(dest_path, 'w') as outfile:
    yaml.dump(workload, outfile, default_flow_style=False)

def usage():
  print 'Usage: '+ sys.argv[0] +' --experiment=<experiment.yaml> --wl_configs=<workload_configs_folder>'

def read_args(argv):
  arguments = {}
  try:
    opts, args = getopt.getopt(argv[1:],"he:w:",["help", "experiment=", "wl_configs="])
    for opt, arg in opts:
      if opt in ("-h", "--help"):
        usage()
        sys.exit(2)
      if opt in ("-e", "--experiment"):
        arguments['experiment'] = arg.rstrip('/')
      elif opt in ("-w", "--wl_configs"):
        arguments['wl_configs'] = arg.rstrip('/')
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  return arguments

def get_experiment_path(arguments):
  experiment_key = 'experiment'
  if not experiment_key in arguments.keys():
    print 'Missing the path to the experiment definition.'
    usage()
    sys.exit(2)
  return arguments[experiment_key]

def get_wl_configs_path(arguments):
  wl_configs_key = 'wl_configs'
  if not wl_configs_key in arguments.keys():
    print 'Missing the path to the wl_configs dir.'
    usage()
    sys.exit(2)
  return arguments[wl_configs_key]

if __name__ == '__main__':
  arguments = read_args(sys.argv)
  experiment_path = get_experiment_path(arguments)
  wl_configs_path = get_wl_configs_path(arguments)
  result = split_experiment(experiment_path, wl_configs_path)

