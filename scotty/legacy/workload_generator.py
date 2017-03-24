import logging
import os
import git
import subprocess
import sys

import scotty.utils as utils

LOG = logging.getLogger(__name__)

class Workflow(object):
    def __init__(self, options):
        self._options = options

    def run(self):
        self._checkout()
        self._workload_run()
 
    def _checkout(self):
        LOG.info('Checkout workload')
        if self._options.skip_checkout:
            LOG.info('    found option --skip-checkout (-s): skip checkout workload')
            workspace = os.path.abspath(self._options.workspace)
            self._workload = Workload(workspace, '__dummy__')
            LOG.info('    workspace: {}'.format(self._workload.workspace))
            return
        workspace = os.path.abspath(self._options.workspace)
        gerrit_url = utils.Config().get('gerrit', 'host') + '/p/'
        try:
            project  = os.environ['ZUUL_PROJECT']
            zuul_url = os.environ['ZUUL_URL']
            zuul_ref = os.environ['ZUUL_REF']
        except KeyError as e:
            LOG.error('Missing environment key ({})'.format(e))
            sys.exit(-1)
        self._workload = Workload(workspace, project)
        LOG.info('    project: {}'.format(self._workload.project))
        LOG.info('    source: {}'.format(gerrit_url + self._workload.project))
        LOG.info('    workspace: {}'.format(self._workload.workspace))
        self._workload.checkout(gerrit_url, zuul_url, zuul_ref)
    
    def _workload_run(self):
        # TODO run workload  
        LOG.info('Run workload') 
        if self._options.not_run:
            LOG.info('    found option --not-run (-n): skip run workload')
            return
        self._workload.run(self._workload.workspace)

class Workload(object):
    def __init__(self, workspace, project):
        self.project = project
        self.workspace = workspace
        self.config = {}
        
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
        workload_path = self.workspace + '/test'
        if not os.path.isdir(workload_path):
            workload_path = self.workspace + '/samples'
        if os.path.isfile(workload_path + '/workload.yaml'):
            workload_path += '/workload.yaml'
        else:
            workload_path += '/workload.yml'
        subprocess.check_call([
             './run.py',
             '-w', workload_path,
             '-d', data_path],
             cwd=self.workspace)
