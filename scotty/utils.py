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

        def get(self, section, option, abspath=False):
            value = self._config.get(section, option)
            if abspath: value = self._abspath(value)
            return value 

    instance = None
    def __init__(self):
        if not Config.instance:
            Config.instance = Config.__Config()

    def __getattr__(self, name):
        return getattr(self.instance, name)
