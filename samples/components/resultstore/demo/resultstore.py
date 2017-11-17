import logging

from scotty import utils

logger = logging.getLogger(__name__)

def submit(context):
   resultstore = context.v1.resultstore
   experiment_helper = utils.ExperimentHelper(context)
   workloads = experiment_helper.get_workloads()
   experiment_starttime = experiment_helper.get_experiment_starttime()
   logger.info('Hey there,')
   logger.info('I\'m resultstore {}'.format(resultstore.name))
   logger.info('Experiment starttime: {}'.format(experiment_starttime))
   for workload in workloads.itervalues():
       logger.info('Workload {} starttime: {}'.format(workload.name, workload.starttime))
   
