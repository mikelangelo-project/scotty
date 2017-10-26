import logging

from scotty import utils

logger = logging.getLogger(__name__)

def run(context):
    workload = context.v1.workload
    experiment_helper = utils.ExperimentHelper(context)
    demo_resource = experiment_helper.get_resource(workload.resources['demo_res'])
    logger.info('{}'.format(workload.params['greeting']))
    logger.info('I\'m workload generator {}'.format(workload.name))
    logger.info('Resource endpoint: {}'.format(demo_resource.endpoint))
    result = 'result'
    return result

def clean(context):
    pass
