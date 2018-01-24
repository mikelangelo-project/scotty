import logging

from scotty.cmd.base import CommandParser
from scotty.cmd.base import CommandRegistry
from scotty.workflows.experiment import ExperimentPerformWorkflow
from scotty.workflows.experiment import ExperimentCleanWorkflow

logger = logging.getLogger(__name__)


@CommandRegistry.parser
class ExperimentParser(CommandParser):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(
            help='Action',
            dest='action')
        performparser = subparsers.add_parser('perform')
        PerformParser().add_arguments(performparser)
        cleanparser = subparsers.add_parser('clean')
        CleanParser().add_arguments(cleanparser)


class CleanParser(CommandParser):
    def add_arguments(self, parser):
        parser.add_argument(
            '-w', '--workspace',
            help='Path to experiment workspace',
            dest='workspace',
            action='store',
            default='./')

class PerformParser(CommandParser):
    def add_arguments(self, parser):
        parser.add_argument(
            '-w', '--workspace',
            help='Path to experiment workspace',
            dest='workspace',
            action='store',
            default='./')
        parser.add_argument(
            '-c', '--config',
            help='Path to experiment config',
            dest='config',
            action='store',
            default=None)
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
        elif self.options.action == 'clean':
            workflow = ExperimentCleanWorkflow(self.options)
            workflow.run()
