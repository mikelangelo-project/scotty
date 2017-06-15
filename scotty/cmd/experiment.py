import logging

from scotty.cmd.base import CommandParser
from scotty.cmd.base import CommandRegistry
from scotty.workflows import ExperimentPerformWorkflow

logger = logging.getLogger(__name__)


@CommandRegistry.parser
class ExperimentParser(CommandParser):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            help='Action',
            dest='action')
        performparser = subparsers.add_parser('perform')
        PerformParser().add_arguments(performparser)


class PerformParser(CommandParser):
    def add_arguments(self, parser):
        parser.add_argument(
            '-w', '--workspace',
            help='Path to experiment workspace',
            dest='workspace',
            action='store',
            default='./')
        parser.add_argument(
            '-m', '--mock',
            help='Do not run the workloads',
            dest='mock',
            default=False,
            action='store_true')


@CommandRegistry.command
class Command(object):
    def __init__(self, options):
        self.options = options

    def execute(self):
        if self.options.action == 'perform':
            workflow = ExperimentPerformWorkflow(self.options)
            workflow.run()
