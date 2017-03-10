import logging

COMMAND = 'legacy'

def setup_parser(parent_parser):
    subparser = parent_parser.add_subparsers(
        help = 'Run legacy scrips',
        dest = 'command')
    parser = subparser.add_parser(COMMAND)
    parser.add_argument(
        '-p', '-pipeline',
        help = 'Executed pipeline',
        choices = ['experiment', 'workload_generator'],
        action = 'store',
        required = True) 

def run( args):
    logging.info('run legacy script')
