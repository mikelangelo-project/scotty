import logging

from scotty import utils

logger = logging.getLogger(__name__)

def endpoint(context):
    endpoint = {
        'url': 'https://demo.resource',
        'user': 'scotty',
        'password': '********'
    }
    return endpoint

def deploy(context):
    resource = context.v1.resource
    logger.info('Hey there,')
    logger.info('I\'m resource generator {}'.format(resource.name))

def clean(context):
    pass
