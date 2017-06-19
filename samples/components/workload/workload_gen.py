import logging


logger = logging.getLogger(__name__)


def run(context):
    name = context.v1.self.name
    print 'Hey there,'
    print 'my name is {name} '.format(name=name),
    print 'and I\'m running a dummy workload with my config:'
    print '{context}'.format(context=context.v1.self.config)
    print 'params'
    print '{params}'.format(params=context.v1.self.config['params'])
    raise Exception('TestException')
