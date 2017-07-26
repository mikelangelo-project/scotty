import logging

from scotty.cmd.base import CommandParser
from scotty.cmd.base import CommandRegistry
from scotty.workflows import WorkloadInitWorkflow
from scotty.core.exceptions import ScottyException

logger = logging.getLogger(__name__)


@CommandRegistry.parser
class WorkloadParser(CommandParser):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            help='Action',
            dest='action')
        initparser = subparsers.add_parser('init')
        InitParser().add_arguments(initparser)

class InitParser(CommandParser):
    def add_arguments(self, parser):
        parser.add_argument(
            'directory', 
            nargs='?',
            metavar='directory', 
            type=str,
            help="Directory where the workload repo will be created (Default:'./')",
            default='./')


@CommandRegistry.command
class Command(object):
    def __init__(self, options):
        self.options = options

    def execute(self):
        if self.options.action == 'init':
            try:
                workflow = WorkloadInitWorkflow(self.options)
                workflow.run()
            except ScottyException as err:
                logger.error(err)
