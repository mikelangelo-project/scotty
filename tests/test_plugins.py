import unittest

import scotty.plugins as plugins


class TestPluginMechanism(unittest.TestCase):
    def test_load_plugin(self):
        plugin = plugins.PluginLoader.load_by_path('samples/workload_gen_dummy.py', {})
