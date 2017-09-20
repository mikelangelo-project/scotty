# -*- coding: utf-8 -*-
import unittest
import logging

import scotty.cmd.experiment
import mock

from tests.test_cmd import CommandTest

logger = logging.getLogger(__name__)


class ExperimentCommandTest(unittest.TestCase, CommandTest):
    @mock.patch('scotty.workflows.ExperimentPerformWorkflow.run')
    def test_init(self, workflow_run_mock):
        self.command_class = scotty.cmd.experiment.Command
        self.args = ['experiment', 'perform']
        self._test_parser()
        workflow_run_mock.assert_called_once()
