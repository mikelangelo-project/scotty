import logging


logger = logging.getLogger(__name__)


def run(context):
    workload_config = context.v1.workload.config
    workload_params = workload_config['params']
    print '{}'.format(workload_params['greeting'])
    print 'I\'m a workload generator, my name is {} '.format(context.v1.workload.name),
    print 'and I\'m running a demo workload with my config:'
    print '{}'.format(workload_config)
