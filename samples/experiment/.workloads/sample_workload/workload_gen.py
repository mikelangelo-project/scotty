import logging


logger = logging.getLogger(__name__)


def run(context):
    name = context.v1.workload_config.name
    print 'Hey there,'
    print 'my name is {name} '.format(name=name),
    print 'and I\'m running a dummy workload with my config:'
    print '{context}'.format(context=context.v1.workload_config._dict)
    print 'params'
    print '{params}'.format(params=context.v1.workload_config.params)
    raise Exception('TestException')
