import logging

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
        # TODO checkout workload change
        # TODO copy workload.yaml from workload test directory
        LOG.info('Checkout workload')
    
    def _workload_run(self):
        # TODO run workload  
        LOG.info('Run workload') 
        if self._args.getargs().not_run:
            LOG.info('    found option --not-run (-n): skip run workload')
            return
