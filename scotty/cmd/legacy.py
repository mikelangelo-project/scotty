from scotty.cmd.base import CommandParser
from scotty.cmd.base import CommandBuilder
from scotty.cmd.base import CommandRegistry
import scotty.legacy.workload_generator
import scotty.legacy.experiment


@CommandRegistry.addparser
class LegacyParser(CommandParser):
    def add_arguments(self, parser):
        subparser = parser.add_subparsers(
            help='Pipeline',
            dest='pipeline')
        ExperimentParser().add_arguments(
            subparser.add_parser('experiment'))
        WorkloadParser().add_arguments(
            subparser.add_parser('workload_generator'))


class ExperimentParser(CommandParser):
    def add_arguments(self, parser):
        parser.add_argument(
            '-w', '--workspace',
            help='Path to experiment workspace',
            dest='workspace',
            action='store',
            required=True)
        parser.add_argument(
            '-n', '--not-run',
            help='Do not run workloads',
            dest='not_run',
            default=False,
            action='store_true')


class WorkloadParser(CommandParser):
    def add_arguments(self, parser):
        parser.add_argument(
            '-w', '--workspace',
            help='Path to workload workspace',
            dest='workspace',
            action='store',
            required=True)
        parser.add_argument(
            '-n', '--not-run',
            help='Do not run workload',
            dest='not_run',
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
        if 'experiment' in self.options.pipeline:
            workflow = scotty.legacy.experiment.Workflow(self.options)
        elif 'workload_generator' in self.options.pipeline:
            workflow = scotty.legacy.workload_generator.Workflow(self.options)
        workflow.run()


@CommandRegistry.addbuilder
class CommandBuilder(CommandBuilder):
    command_class = Command
