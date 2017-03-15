import logging
import sys
import os

import scotty.legacy.workload_generator
import scotty.legacy.experiment

COMMAND = 'legacy'
HELP = 'Run legacy scrips'

def setup_parser(parser):
    subparser = parser.add_subparsers(
        help = 'dgshsh',
        dest = 'pipeline')
    exp_parser = subparser.add_parser('experiment')
    exp_parser.add_argument(
        '-e', '--experiment_path',
        help = 'Path to experiment',
        dest = 'experiment_path',
        action = 'store',
        required = True)
    wl_gen_parser = subparser.add_parser('workload_generator')
    wl_gen_parser.add_argument(
        '-w', '--workload_path',
        help = 'Path to workload',
        dest = 'workload_path',
        action = 'store',
        required = True)

def main(args):
    logging.info('run legacy scripts')
    pipeline = args.getargs().pipeline
    getattr(sys.modules[__name__], pipeline)(args)

def experiment(args):
    scotty.legacy.experiment.Workflow(args).run()

def workload_generator(args):
    scotty.legacy.workload_generator.WorkloadGenerator(args).main()
