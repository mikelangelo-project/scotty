import logging
import os.path

import yaml

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
            self._checkout_workload()
            self._run_workload()

    # TODO implement
    def _checkout_workload(self):
        logging.info('Checking out workload')
        pass
        logging.info('Checkout done')
    
    def _run_workload(self):
        workload_path = self._get_workload_path()
        logger.info('running the workload in {workspace}'.format(workspace=workload_path))
        workload_conf = self._load_workload_conf()
        workload_name = workload_conf['workload']['name']
        workload_ = workload.WorkloadLoader.load_by_path(workload_path, workload_name)
        if not self.options.mock:
            context = {'workload_conf': workload_conf}
            workload_.run(context)

    def _get_workload_path(self):
        workspace_path = self._get_workspace_path()
        workload_path = workspace_path + '/' + 'workload_gen.py'
        return workload_path

    def _get_workspace_path(self):
        workspace = self.options.workspace
        workspace_abs = os.path.abspath(workspace)
        return workspace_abs

    def _load_workload_conf(self):
        conf_path = self._get_conf_path()
        logging.info('loading workload conf: {}'.format(conf_path))
        conf = None
        with open(conf_path, 'r') as conf_file:
            conf = yaml.load(conf_file)
        logging.info(conf)
        return conf

    def _get_conf_path(self):
        workspace_path = self._get_workspace_path()
        conf_path = workspace_path + '/' + 'workload.yaml'
        return conf_path


@CommandRegistry.addbuilder
class CommandBuilder(CommandBuilder):
    command_class = Command
