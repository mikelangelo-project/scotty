import logging

from scotty import utils

logger = logging.getLogger(__name__)

def submit(context):
   resultstore = context.v1.resultstore
   logger.info('Hey there,')
   logger.info('I\'m resultstore {}'.format(resultstore.name))
