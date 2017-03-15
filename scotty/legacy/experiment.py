import logging
import os
import sys
import yaml
import git
import subprocess

LOG = logging.getLogger(__name__)

class Workflow(object):
    def __init__(self, args):
        self._args = args        

    def run(self):
        self._checkout()
        self._load_experiment()
  	self._split_experiment()
	self._workload_run()

    def _checkout(self):
        # TODO run gerrit-git-prep.sh from shell
        LOG.info('Checkout experiment')
        self._experiment = Experiment(self._args.getargs().experiment_path)        
        source = 'gerrit bla'
        LOG.info('    source: {}'.format(source))
        LOG.info('    target: {}'.format(self._experiment.path))
 
    def _load_experiment(self):
        LOG.info('Load experiment')
        self._experiment.load()
        LOG.info('    workloads: {}'.format(self._experiment.count_workloads()))

    def _split_experiment(self):
        LOG.info('Split experiment into workloads')
        self._experiment.split()
        for name, workload in self._experiment.iter_workloads():
            source = 'https://gerrit/p/workload_gen/' + workload.generator
            LOG.info('    workload: {}'.format(name))
            LOG.info('    source: {}'.format(source))
            LOG.info('    target: {}'.format(workload.path))
            if workload.checkout(source):
                LOG.info('    clone new workload')
            else:
                LOG.info('    pull existing workload')
	    LOG.info('    write {}'.format(workload.definition_path))
            workload.save()

    def _workload_run(self):
        # TODO run all workloads in experiment
        LOG.info('Run experiment workloads')
        for name, workload in self._experiment.iter_workloads():
            LOG.info('    run {}'.format(name))
            workload.run(self._experiment.path)

class Experiment(object):
    def __init__(self, path):
        self.path = path
        self.config = {}
        self.config_path = os.path.abspath(path + '/experiment.yaml')
        self.workloads = {}
        self.workloads_path = os.path.abspath(path + '/.workloads/')

    def load(self):
        try:
            stream = open(self.config_path, 'r')
            self.config = yaml.load(stream)
        except IOError, e:
            LOG.error('{}'.format(e))
            sys.exit(-1)
  
    def split(self):
        if not os.path.isdir(self.workloads_path):
            os.mkdir(self.workloads_path)
        for workload in self.config:
            name = workload['workload']['name']
            path = os.path.normpath(self.workloads_path + '/' + name)
            self.workloads[name] = Workload(path, workload)

    def count_workloads(self):
        return len(self.config)

    def iter_workloads(self):
        return self.workloads.iteritems()

class Workload(object):
    def __init__(self, path, definition):
        self.path = path
        self.definition = definition
        self.definition_path = self.path + '/workload.yaml'
        self.name = definition['workload']['name']
        self.generator = definition['workload'].get('generator', self.name)
    
    def save(self):
        with open(self.definition_path, 'w') as file:
            yaml.dump(self.definition, file, default_flow_style=False)
 
    def checkout(self, source):
        g = git.cmd.Git(self.path)
        new = False
        if os.path.isdir(self.path + '/.git'):
            new = False
            g.pull()
        else:
            if not os.path.isdir(self.path):
                os.mkdir(self.path)
            new = True
            g.clone(source, '.')
        return new

    def run(self, data_path):
        subprocess.check_call([
             './run.py', 
             '-w', './workload.yaml', 
             '-d', data_path], 
             cwd=self.path)
