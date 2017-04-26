import unittest

import mock

from scotty.experiment import CheckoutManager
from scotty.experiment import Workspace


class CheckoutManagerClass(unittest.TestCase):
    @mock.patch(
        'git.cmd')
    def test_checkout(self, git_mock):
        workspace = Workspace('samples/experiment')
        checkout_manager = CheckoutManager()
        checkout_manager.checkout(
            workspace=workspace,
            project='project',
            origin_url='origin_url',
            update_url='update_url',
            ref='ref')
        unpacked_calls = self._unpack_calls(git_mock.mock_calls)
        expected_calls = [('Git', ('samples/experiment',), {}),
                          ('Git().clone', ('origin_urlproject', '.'), {}),
                          ('Git().remote', ('update',), {}),
                          ('Git().reset', ('--hard',), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {}),
                          ('Git().fetch', ('update_urlproject', 'ref'), {}),
                          ('Git().checkout', ('FETCH_HEAD',), {}),
                          ('Git().reset', ('--hard', 'FETCH_HEAD'), {}),
                          ('Git().clean', ('-x', '-f', '-d', '-q'), {})]
        self.assertEquals(unpacked_calls, expected_calls)

    def _unpack_calls(self, mock_calls):
        unpacked_calls = []
        for mock_call in mock_calls:
            name, args, kwargs = mock_call
            unpacked_calls.append((name, args, kwargs))
        return unpacked_calls
