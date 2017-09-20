import unittest

import mock

from scotty.config import ScottyConfig
from scotty.core.exceptions import ScottyException


class ScottyConfigTest(unittest.TestCase):
    def test_scotty_config_constructor(self):
        scotty_config = ScottyConfig()
        self.assertIsNotNone(scotty_config)

    @mock.patch('scotty.config.ScottyConfig._find_base_dir')
    def test_config_log_fields(self, base_dir_mock):
        base_dir_mock.return_value = 'samples/etc/'
        scotty_config = ScottyConfig()
        log_dir = scotty_config.get('logging', 'log_dir')
        self.assertEquals(log_dir, '../log')
        log_file = scotty_config.get('logging', 'log_file')
        self.assertEquals(log_file, 'scotty.log')
        log_format = scotty_config.get('logging', 'log_format')
        self.assertEquals(log_format,
                          '%(asctime)s - %(levelname)s:%(name)s: %(message)s')
        log_level = scotty_config.get('logging', 'log_level')
        self.assertEquals(log_level, 'debug')
        self._assert_num_options(scotty_config, 'logging', 4)

    def test_scotty_config_gerrit_fields(self):
        scotty_config = ScottyConfig()
        host = scotty_config.get('gerrit', 'host')
        self.assertEquals(host, 'https://gerrit')
        self._assert_num_options(scotty_config, 'gerrit', 1)

    def test_config_osmod_fields(self):
        scotty_config = ScottyConfig()
        endpoint = scotty_config.get('osmod', 'endpoint')
        self.assertEquals(endpoint,
                          'https://api.liberty.mikelangelo.gwdg.de:8020')
        username = scotty_config.get('osmod', 'username')
        self.assertEquals(username, 'us3r')
        password = scotty_config.get('osmod', 'password')
        self.assertEquals(password, 'p4ss')
        self._assert_num_options(scotty_config, 'osmod', 3)

    def _assert_num_options(self, scotty_config, section, num_options):
        options = scotty_config._config.options(section)
        self.assertEquals(len(options), num_options)

    @mock.patch('os.path.isfile')
    def test_find_base_dir(self, isfile_mock):
        isfile_mock.return_value = True
        scotty_config = ScottyConfig()
        base_dir = scotty_config._find_base_dir()
        self.assertEquals(base_dir, '/etc/scotty/')

    @mock.patch('os.path.isfile')
    def test_no_scotty_config_file(self, isfile_mock):
        isfile_mock.return_value = False
        with self.assertRaises(ScottyException):
            ScottyConfig()
