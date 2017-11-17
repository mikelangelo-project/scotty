import logging

from scotty import utils

logger = logging.getLogger(__name__)

def collect(context):
    systemcollector = context.v1.systemcollector
    logger.info('Hey there,')
    logger.info('I\'m systemcollector {}'.format(systemcollector))
