import logging
import sys
import os

import scotty.legacy.workload_generator
import scotty.legacy.experiment

COMMAND = 'legacy'
HELP = 'Run legacy scrips'

LOG = logging.getLogger(__name__)

def setup_parser(parser):
    subparser = parser.add_subparsers(
        help = 'dgshsh',
        dest = 'pipeline')
    exp_parser = subparser.add_parser('experiment')
    exp_parser.add_argument(
        '-w', '--workspace',
        help = 'Path to experiment workspace',
        dest = 'workspace',
        action = 'store',
        required = True)
    exp_parser.add_argument(
        '-n', '--not-run',
        help = 'Do not run workloads',
        dest = 'not_run',
        default = False,
        action = 'store_true')
    wl_gen_parser = subparser.add_parser('workload_generator')
    wl_gen_parser.add_argument(
        '-w', '--workload_path',
        help = 'Path to workload',
        dest = 'workload_path',
        action = 'store',
        required = True)
    wl_gen_parser.add_argument(
        '-n', '--not-run',
        help = 'Do not run workload',
        dest = 'not_run',
        default = False,
        action = 'store_true')

def main(args):
    LOG.info('run legacy scripts')
    pipeline = args.getargs().pipeline
    getattr(sys.modules[__name__], pipeline)(args)

def experiment(args):
    scotty.legacy.experiment.Workflow(args).run()

def workload_generator(args):
    scotty.legacy.workload_generator.Workflow(args).run()
