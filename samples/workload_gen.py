import logging


logger = logging.getLogger(__name__)


def run(context):
    name = context['workload_conf']['workload']['name']
    print 'Hey there,\nmy name is {name} and I\'m running a dummy workload with my context:\n{context}'.format(name=name, context=context)
    return context
