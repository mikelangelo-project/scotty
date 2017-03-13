import logging
import os
import sys
import yaml

LOG = logging.getLogger(__name__)

class Experiment(object):
    def __init__(self, args):
        self._args = args        

    def main(self):
        self._checkout()
        self._load_expconfig()
        self._split()
  	self._workload_checkout()
	self._workload_run()

    def _checkout(self):
        # TODO run gerrit-git-prep.sh from shell
        LOG.info('Checkout experiment')
 
    def _load_expconfig(self):
        LOG.info('Load experiment config')
        self._exp_config = ExpConfig(os.path.abspath(self._args.getargs().experiment_path + '/experiment.yaml'))

    def _split(self):
        # TODO run epxeriment-split.py from shell
        LOG.info('Split experiment yaml into workloads')

    def _workload_checkout(self):
        # TODO checkout all workloads in experiment
        LOG.info('Checkout experiment workloads')
 
    def _workload_run(self):
        # TODO run all workloads in experiment
        LOG.info('Run experiment workloads')

class ExpConfig(object):
    def __init__(self, path):
        self._path = path
        self._load()

    def _load(self):
        try:
            stream = open(self._path, 'r')
            self._dict = yaml.load(stream)
        except IOError, e:
            LOG.error('{}'.format(e))
            sys.exit(-1)
  
    def _getpath():
        self._path

    def _getargs():
        self._dict
