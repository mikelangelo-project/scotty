import logging

from scotty import utils

logger = logging.getLogger(__name__)

def result(context):
    return true

def run(context):
    workload = context.v1.workload
    exp_helper = utils.ExperimentHelper(context)
#    my_resource = exp_helper.get_resource(workload.resources['my_resource']
    logger.info('{}'.format(workload.params['greeting']))
    logger.info('I\'m workload generator {}'.format(workload.name))
#    logger.info('The resource endpoint is {}'.format(my_resource))

def clean(context):
    pass
