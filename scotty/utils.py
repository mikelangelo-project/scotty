import argparse
import logging
import os
import ConfigParser

import scotty

class Args(object):
    def __init__(self, args):
        self._setup()
        self._args = self._parser.parse_args(args)

    def _setup(self):
        self._parser = argparse.ArgumentParser()
        for key, command in scotty.cli.iter_commands():
	    self._setup_command(command)
     
    def _setup_command(self, command):
        subparser = self._parser.add_subparsers(
	    help = command.HELP,
            dest = 'command')
        cmd_parser = subparser.add_parser(command.COMMAND)
        command.setup_parser(cmd_parser)
            
    def getargs(self):
        return self._args

    def exec_command(self):
        scotty.cli.COMMANDS[self._args.command].main(self)

class Config(object):
    class __Config:
        _raw_config = {
            'DEFAULT' : {
                'log_format' : True}}
        def __init__(self):
            script_dir = os.path.dirname(os.path.realpath(__file__))
            self._base_dir = self._find_base_dir()
            self._path =  os.path.normpath(self._base_dir + '/scotty.conf')
            self._load()

        def _find_base_dir(self):
            if os.path.isfile('/etc/scotty/scotty.conf'):
                return '/etc/scotty/'
            else:
                script_dir = os.path.dirname(os.path.realpath(__file__))
                base_dir = os.path.normpath(script_dir + '/../etc/')
                config_path = os.path.normpath(base_dir + '/scotty.conf')
                if os.path.isfile(config_path):
                    return base_dir
                else:
                    raise Exception('Found no configuration for scotty (/etc/scotty/scotty.conf or ./python-scotty/etc/scotty.conf)')

        def _load(self):
            self._config = ConfigParser.ConfigParser()
            self._config.read(self._path)

        def _abspath(self, path):
            if not os.path.isabs(path):
                path = os.path.normpath(self._base_dir + '/'+ path)
            return path
 
        def _is_raw(self, section, option):
            if section in self._raw_config:
                return self._raw_config[section].get(option, False)

        def get(self, section, option, abspath=False):
            value = self._config.get(section, option, self._is_raw(section, option))
            if abspath: value = self._abspath(value)
            return value 

    instance = None
    def __init__(self):
        if not Config.instance:
            Config.instance = Config.__Config()

    def __getattr__(self, name):
        return getattr(self.instance, name)

def setup_logging():
    log_dir    = Config().get('DEFAULT', 'log_dir', True)
    log_file   = Config().get('DEFAULT', 'log_file')
    log_format = Config().get('DEFAULT', 'log_format')
    log_level  = Config().get('DEFAULT', 'log_level')

    logging.getLogger().setLevel(log_level.upper())
    file_handler = logging.FileHandler(log_dir + '/' + log_file)
    file_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(stream_handler)
