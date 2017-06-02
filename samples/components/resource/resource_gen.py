import logging

logger = logging.getLogger(__name__)

def deploy(context):
    name = context.v1.resource_config['name']
    print 'Hey there,'
    print 'my name is {name} '.format(name=name),
    print 'and I\'m deploy a dummy resource with my config:'
    print '{config}'.format(config=context.v1.resource_config)
    raise Exception('TestException')
