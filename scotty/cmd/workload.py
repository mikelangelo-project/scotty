import os.path

from scotty.cmd.base import CommandParser
from scotty.cmd.base import CommandBuilder
from scotty.cmd.base import CommandRegistry
from scotty import workload


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
        # TODO checkout out the workload
        # TODO implement skipping the checkout
        if self.options.action == 'run':
            workspace = self.options.workspace
            workspace_abs = os.path.abspath(workspace)
            print 'running the workload in {workspace}'.format(workspace=workspace_abs)
            # TODO clean the path
            workload_path = workspace_abs + '/' + 'workload_gen.py'
            # TODO name
            workload_ = workload.WorkloadLoader.load_by_path(workload_path)
            if not self.options.mock:
                # TODO Create context
                context = {}
                workload_.run(context)


@CommandRegistry.addbuilder
class CommandBuilder(CommandBuilder):
    command_class = Command
