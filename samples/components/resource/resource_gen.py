import logging

logger = logging.getLogger(__name__)

def endpoint(context):
    endpoint = {
        'url': 'https://demo.resouces',
        'user': 'scotty',
        'password': '********',
    }
    return endpoint

def deploy(context):
    name = context.v1.resource.name
    print 'Hey there,'
    print 'my name is {} '.format(name),
    print 'and I\'m deploy a dummy resource with my config:'
    print '{}'.format(context.v1.resource.config)
    raise Exception('TestException')

def clean(context):
    pass
