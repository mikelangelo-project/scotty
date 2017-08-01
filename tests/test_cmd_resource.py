# -*- coding: utf-8 -*-

import unittest

import scotty.cmd.resource

from tests.test_cmd import CommandTest


class ResourceCommandTest(unittest.TestCase, CommandTest):
    def test_init(self):
        self.command_class = scotty.cmd.resource.Command
        self.args = ['resource', 'init']
        self._test_parser()
