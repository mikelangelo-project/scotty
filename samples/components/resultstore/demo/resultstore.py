import logging

from scotty import utils

logger = logging.getLogger(__name__)

def submit(context):
   resultstore = context.v1.resultstore
   experiment_helper = utils.ExperimentHelper(context)
   workloads = experiment_helper.get_workloads()
   logger.info('Hey there,')
   logger.info('I\'m resultstore {}'.format(resultstore.name))
   for workload in workloads.itervalues():
       logger.info('Workload {} starttime: {}'.format(workload.name, workload.starttime))
   
