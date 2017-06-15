import logging

from scotty.cmd.base import CommandParser
from scotty.cmd.base import CommandRegistry
from scotty.workflows import WorkloadRunWorkflow

logger = logging.getLogger(__name__)


@CommandRegistry.parser
class WorkloadParser(CommandParser):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            help='Action',
            dest='action')
        runparser = subparsers.add_parser('run')
        RunParser().add_arguments(runparser)


class RunParser(CommandParser):
    def add_arguments(self, parser):
        parser.add_argument(
            '-w', '--workspace',
            help='Path to workload workspace',
            dest='workspace',
            action='store',
            default='./')
        parser.add_argument(
            '-c', '--config',
            help='Path to workload config',
            dest='config',
            action='store',
            required=True)
        parser.add_argument(
            '-m', '--mock',
            help='Do not run the workload',
            dest='mock',
            default=False,
            action='store_true')


@CommandRegistry.command
class Command(object):
    def __init__(self, options):
        self.options = options

    def execute(self):
        if self.options.action == 'run':
            workflow = WorkloadRunWorkflow(self.options)
            workflow.run()
