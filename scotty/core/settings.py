import os
import json

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
    _config_type = {
        'logging': {'log_format': 'raw'},
        'resultstores': {'stores': 'json'},
        'owncloud': {
            'enable': 'boolean',
            'params': 'json'
        },
    }

    def __init__(self, config_parser):
        self._config_parser = config_parser

    def get(self, section, option):
        type_ = self._type(section, option)
        parse_method_name = '_parse_{}'.format(type_)
        parse_method = getattr(self, parse_method_name)
        value = parse_method(section, option)
        return value

    def _parse_raw(self, section, option):
        value = self._config_parser.get(section, option, True)
        return value

    def _parse_None(self, section, option):
        value = self._config_parser.get(section, option)
        return value

    def _parse_json(self, section, option):
        value = self._config_parser.get(section, option)
        value = json.loads(value)
        return value

    def _parse_boolean(self, section, option):
        value = self._config_parser.getboolean(section, option)
        return value

    def _type(self, section, option):
        type_ = None
        if section in self._config_type:
             type_ = self._config_type[section].get(option, None)
        return type_
