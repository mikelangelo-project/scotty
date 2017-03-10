import logging

class Experiment(object):
    def __init__(self, args):
        self._args = args

    def main(self):
        logging.info('Experiment main')
