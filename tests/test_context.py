import unittest

from scotty.core.context import ContextAccessible, ContextComponent
from scotty.core.components import Workload
from scotty.core.exceptions import ScottyException


class ContextAccessibleTest(unittest.TestCase):
    def test_call(self):
        def test_function():
            pass

        context_accessible = ContextAccessible('resource')
        function = context_accessible(test_function)
        self.assertEquals(function, test_function)


class ContextComponentTest(unittest.TestCase):
    def setUp(self):
        self._workload = Workload()

    def test_context_component(self):
        workload = self._workload
        context = ContextComponent(workload)
        with self.assertRaises(ScottyException):
            context.module
