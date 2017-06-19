import logging


logger = logging.getLogger(__name__)


def run(context):
    workload_config = context.v1.self.config
    workload_params = workload_config['params']
    print '{greeting}'.format(greeting=workload_params['greeting'])
    print 'I\'m a workload generator, my name is {name} '.format(name=workload_config['name']),
    print 'and I\'m running a demo workload with my config:'
    print '{workload_config}'.format(workload_config=workload_config)
