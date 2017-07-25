import logging

from scotty.cmd.base import CommandParser
from scotty.cmd.base import CommandRegistry

logger = logging.getLogger(__name__)


@CommandRegistry.parser
class WorkloadParser(CommandParser):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            help='Action',
            dest='action')
        initparser = subparsers.add_parser('init')

@CommandRegistry.command
class Command(object):
    def __init__(self, options):
        self.options = options

    def execute(self):
        if self.options.action == 'init':
            logger.info("Command 'scotty workload init' is not implemented yet")
