import unittest

import mock

import scotty.utils as utils


class ConfigTest(unittest.TestCase):
    def test_config_constructor(self):
        config = utils.Config()
        self.assertIsNotNone(config)

    @mock.patch('scotty.utils.Config._find_base_dir')
    def test_config_log_fields(self, base_dir_mock):
        base_dir_mock.return_value = 'samples/etc/'
        config = utils.Config()
        log_dir = config.get('logging', 'log_dir')
        self.assertEquals(log_dir, '../log')
        log_file = config.get('logging', 'log_file')
        self.assertEquals(log_file, 'scotty.log')
        log_format = config.get('logging', 'log_format')
        self.assertEquals(log_format,
                          '%(asctime)s - %(levelname)s:%(name)s: %(message)s')
        log_level = config.get('logging', 'log_level')
        self.assertEquals(log_level, 'debug')
        self._assert_num_options(config, 'logging', 4)

    def test_config_gerrit_fields(self):
        config = utils.Config()
        host = config.get('gerrit', 'host')
        self.assertEquals(host, 'https://gerrit')
        self._assert_num_options(config, 'gerrit', 1)

    def test_config_osmod_fields(self):
        config = utils.Config()
        endpoint = config.get('osmod', 'endpoint')
        self.assertEquals(endpoint,
                          'https://api.liberty.mikelangelo.gwdg.de:8020')
        username = config.get('osmod', 'username')
        self.assertEquals(username, 'us3r')
        password = config.get('osmod', 'password')
        self.assertEquals(password, 'p4ss')
        self._assert_num_options(config, 'osmod', 3)

    def _assert_num_options(self, config, section, num_options):
        options = config._config.options(section)
        self.assertEquals(len(options), num_options)

    @mock.patch('os.path.isfile')
    def test_find_base_dir(self, isfile_mock):
        isfile_mock.return_value = True
        config = utils.Config()
        base_dir = config._find_base_dir()
        self.assertEquals(base_dir, '/etc/scotty/')

    @mock.patch('os.path.isfile')
    def test_no_config_file(self, isfile_mock):
        isfile_mock.return_value = False
        with self.assertRaises(Exception):
            utils.Config()
