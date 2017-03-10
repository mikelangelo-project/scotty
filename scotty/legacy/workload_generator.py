import logging

class WorkloadGenerator(object):
    def __init__(self, args):
        self._args = args

    def main(self):
        logging.info('Workload generator main')
