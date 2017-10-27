import os

import ConfigParser

from scotty.core.exceptions import ScottyException


def load_settings():
    global settings
    path = get_config_path()
    config_parser = ConfigParser.ConfigParser() 
    config_parser.read(path)
    settings = ScottyConfig(config_parser)
    return settings

def get(section, option):
    if not 'settings' in globals():
        load_settings()
    setting_value = settings.get(section, option)
    return setting_value

def get_config_path():
    path = get_etc_config_path()
    path = path or get_local_config_path()
    return path

def get_etc_config_path():
    if os.path.isfile('/etc/scotty/scotty.conf'):
        return '/etc/scotty/scotty.conf'

def get_local_config_path():
    config_path = os.path.join(os.path.dirname(__file__), '../../etc', 'scotty.conf')
    config_path = os.path.normpath(config_path)
    return config_path

class ScottyConfig(object):
    _raw_config = {'logging': {'log_format': True}}

    def __init__(self, config_parser):
        self._config_parser = config_parser

    def get(self, section, option):
        is_raw = self._is_raw(section, option)
        value = self._config_parser.get(section, option, is_raw)
        return value

    def _is_raw(self, section, option):
        if section in self._raw_config:
            return self._raw_config[section].get(option, False)
