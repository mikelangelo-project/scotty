import logging
import os
import git
import subprocess

import scotty.utils as utils

LOG = logging.getLogger(__name__)

class Workflow(object):
    def __init__(self, args):
        self._args = args

    def run(self):
        self._checkout()
        self._workload_run()
 
    def _checkout(self):
        # TODO load environment variables
        LOG.info('Checkout workload')
        workspace = os.path.abspath(self._args.getargs().workspace)
        project = 'workload_gen/ycsb_mongodb'
        gerrit_url = utils.Config().get('gerrit', 'host') + '/p/'
        zuul_url = 'http://zuul.ci.mikelangelo.gwdg.de/p/'
	zuul_ref = 'refs/zuul/master/Zf4509a7f11df4f0da83f3700685f39f3'
        self._workload = Workload(workspace, project)
        LOG.info('    project: {}'.format(self._workload.project))
        LOG.info('    source: {}'.format(gerrit_url + self._workload.project))
        LOG.info('    workspace: {}'.format(self._workload.workspace))
        self._workload.checkout(gerrit_url, zuul_url, zuul_ref)
    
    def _workload_run(self):
        # TODO run workload  
        LOG.info('Run workload') 
        if self._args.getargs().not_run:
            LOG.info('    found option --not-run (-n): skip run workload')
            return
        self._workload.run(self._workload.workspace)

class Workload(object):
    def __init__(self, workspace, project):
        self.project = project
        self.workspace = workspace
        self.config = {}
        self.config_path = os.path.abspath(workspace + 'test/workload.yaml')
        
    def load(self):
        try:
            stream = open(self.config_path, 'r')
            self.config = yaml.load(stream)
        except IOError, e:
            LOG.error('{}'.format(e))
            sys.exit(-1)

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

    def run(self, data_path):
        # TODO test if samples or test exist
        subprocess.check_call([
             './run.py',
             '-w', self.workspace + '/samples/workload.yaml',
             '-d', data_path],
             cwd=self.workspace)
