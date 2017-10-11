import logging

logger = logging.getLogger(__name__)


class ReportCollector(object):
    def __init__(self, experiment):
        self.experiment = experiment

    def collect_static(self):
        pass

    def collect(self):
        pass

    def write_report(self):
        pass
