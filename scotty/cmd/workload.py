import logging

from scotty.cmd.base import CommandParser
from scotty.cmd.base import CommandBuilder
from scotty.cmd.base import CommandRegistry
from scotty import workload

logger = logging.getLogger(__name__)


@CommandRegistry.addparser
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
            required=True)
        parser.add_argument(
            '-m', '--mock',
            help='Do not run the workload',
            dest='mock',
            default=False,
            action='store_true')
        parser.add_argument(
            '-s', '--skip-checkout',
            help='Do not checkout workload',
            dest='skip_checkout',
            default=False,
            action='store_true')


class Command(object):
    def __init__(self, options):
        self.options = options

    def execute(self):
        if self.options.action == 'run':
            workflow = workload.Workflow(self.options)
            workflow.run()


@CommandRegistry.addbuilder
class CommandBuilder(CommandBuilder):
    command_class = Command
