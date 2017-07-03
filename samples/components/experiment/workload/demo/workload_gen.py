import logging

from scotty import utils

logger = logging.getLogger(__name__)


def run(context):
    workload = context.v1.workload
    experiment_helper = utils.ExperimentHelper(context)
    demo_resource = experiment_helper.get_resource(workload.resources['demo_res'])
    print '{}'.format(workload.params['greeting'])
    print 'I\'m a workload generator, my name is {} '.format(workload.name),
    print 'and I\'m running a demo workload with my config:'
    print '{}'.format(workload.config)
    print 'The demo resource endpoint is: {}'.format(demo_resource.endpoint)
