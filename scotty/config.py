import os

import ConfigParser

from scotty.core.exceptions import ScottyException


class ScottyConfig(object):
    _raw_config = {'logging': {'log_format': True}}

    def __init__(self):
        self._base_dir = self._find_base_dir()
        path = os.path.join(self._base_dir, 'scotty.conf')
        self._path = os.path.normpath(path)
        self._load()

    def _find_base_dir(self):
        if os.path.isfile('/etc/scotty/scotty.conf'):
            return '/etc/scotty/'
        else:
            return self._get_local_base_dir()

    def _get_local_base_dir(self):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        base_dir = os.path.join(script_dir, '../etc/')
        base_dir = os.path.normpath(base_dir)
        config_path = os.path.join(base_dir, 'scotty.conf')
        config_path = os.path.normpath(config_path)
        return self._verify_base_dir(config_path, base_dir)

    def _verify_base_dir(self, config_path, base_dir):
        if os.path.isfile(config_path):
            return base_dir
        else:
            message = 'Couldn\'t find configuration for scotty in '
            message += '(/etc/scotty/scotty.conf or'
            message += './python-scotty/etc/scotty.conf)'
            raise ScottyException(message)

    def _load(self):
        self._config = ConfigParser.ConfigParser()
        self._config.read(self._path)

    def _abspath(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self._base_dir, path)
            path = os.path.normpath(path)
        return path

    def _is_raw(self, section, option):
        if section in self._raw_config:
            return self._raw_config[section].get(option, False)

    def get(self, section, option, abspath=False):
        value = self._config.get(section, option, self._is_raw(
            section, option))
        if abspath:
            value = self._abspath(value)
        return value
