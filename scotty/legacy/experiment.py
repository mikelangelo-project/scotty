import logging
import os
import sys
import yaml
import git
import subprocess

import scotty.utils as utils

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
        # TODO load environmet variables
        LOG.info('Checkout experiment')
        workspace = os.path.abspath(self._args.getargs().workspace)
        project = 'experiment/ycsb_mongo'
        gerrit_url = utils.Config().get('gerrit', 'host') + '/p/'
        zuul_url = 'http://zuul.ci.mikelangelo.gwdg.de/p/'
        zuul_ref = 'refs/zuul/master/Z1af6a3d986fc4c4fa8f183620c66cfd7'
        self._experiment = Experiment(workspace, project)        
        LOG.info('    project: {}'.format(self._experiment.project))
        LOG.info('    source: {}'.format(gerrit_url + self._experiment.project))
        LOG.info('    workspace: {}'.format(self._experiment.workspace))
        self._experiment.checkout(gerrit_url, zuul_url, zuul_ref)
 
    def _load_experiment(self):
        LOG.info('Load experiment')
        self._experiment.load()
        LOG.info('    workloads: {}'.format(self._experiment.count_workloads()))

    def _split_experiment(self):
        LOG.info('Split experiment into workloads')
        self._experiment.split()
        for name, workload in self._experiment.iter_workloads():
            source = utils.Config().get('gerrit', 'host') 
	    source+= '/p/workload_gen/' + workload.generator
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
        LOG.info('Run experiment workloads')
        if self._args.getargs().not_run:
            LOG.info('    found option --not-run (-n): skip run workloads')
            return    
        for name, workload in self._experiment.iter_workloads():
            LOG.info('    run {}'.format(name))
            workload.run(self._experiment.workspace)

class Experiment(object):
    def __init__(self, workspace, project):
        self.project = project
        self.workspace = workspace
        self.config = {}
        self.config_path = os.path.abspath(workspace + '/experiment.yaml')
        self.workloads = {}
        self.workloads_path = os.path.abspath(workspace + '/.workloads/')

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
 
    def checkout(self, gerrit_url, zuul_url, zuul_ref):
        # TODO implement timed git to have an timeout
        # TODO try again after timeout
        g = git.cmd.Git(self.workspace)
        if not os.path.isdir(self.workspace + '/.git'):
            g.clone(gerrit_url + self.project, '.')
        g.remote('set-url', 'origin', gerrit_url + self.project)
        g.remote('update') # TODO if faild make git gc and try again
        g.reset('--hard')
        g.clean('-x', '-f', '-d', '-q') # TODO try again with sleep one if failed
        if zuul_ref.startswith("refs/tags"):
            # TODO checkout tag
            raise Exception('Not Implemented')
        else:
            g.fetch(zuul_url + self.project, zuul_ref)    
            g.checkout('FETCH_HEAD')
            g.reset('--hard', 'FETCH_HEAD')
        g.clean('-x', '-f', '-d', '-q') # TODO try again with sleep one if failed
        if os.path.isfile(self.workspace + '/.gitmodules'):
           g.submodule('init')
           g.submodule('sync')
           g.submodule('update', '--init')

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
