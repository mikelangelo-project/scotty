# -*- coding: utf-8 -*-
import unittest
import logging

import scotty.cmd.workload

from tests.test_cmd import CommandTest

logger = logging.getLogger(__name__)


class WorkloadCommandTest(unittest.TestCase, CommandTest):
    def test_init(self):
        self.command_class = scotty.cmd.workload.Command
        self.args = ['workload', 'init']
        self._test_parser()
