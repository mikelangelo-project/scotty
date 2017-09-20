import unittest
import mock

import git

from scotty.core.checkout import CheckoutManager
from scotty.core.components import Workload
from scotty.core.exceptions import ScottyException


class CheckoutManagerTest(unittest.TestCase):
    def test_populate(self):
        workload = Workload()
        workload.config = {'generator': 'git://test_host/test_repo'}
        base_path = ''
        CheckoutManager.checkout = mock.MagicMock()
        CheckoutManager.populate(workload, base_path)
        CheckoutManager.checkout.assert_called_once()

    def test_populate_unkown_protocol(self):
        workload = Workload()
        workload.config = {'generator': 'tor://test_host/test_repo'}
        base_path = ''
        CheckoutManager.checkout = mock.MagicMock()
        with self.assertRaises(ScottyException):
            CheckoutManager.populate(workload, base_path)

    def test_copy(self):
        workload = Workload()
        workload.config = {'name': 'test_workload'}
        source_path = '/'
        base_path = '.'
        with self.assertRaises(ScottyException):
            CheckoutManager.copy(workload, source_path, base_path)

    def test_checkout(self):
        git_url = 'git://test_host/test_repo'
        with mock.patch.object(CheckoutManager, '_get_repo', return_value=None) as get_repo_mock:
            with mock.patch.object(CheckoutManager, '_sync_repo', return_value=None) as sync_repo_mock:
                with mock.patch.object(CheckoutManager, '_init_submodules', return_value=None) as init_submodules_mock:
                    CheckoutManager.checkout(git_url, None)
                    sync_repo_mock.assert_called_once()
                    get_repo_mock.assert_called_once()
                    init_submodules_mock.assert_called_once()

    @mock.patch('os.path.isdir')
    def test_is_git_dir(self, isdir_mock):
        isdir_mock.return_value = True
        is_git_dir = CheckoutManager.is_git_dir('')
        self.assertTrue(is_git_dir)
        isdir_mock.assert_called_once_with('/.git')

    def test_get_repo_existing(self):
        git_url = ''
        workspace = mock.MagicMock()
        workspace.path = mock.MagicMock()
        workspace.path.return_value = '/tmp/90209vsji'
        with mock.patch.object(git.Repo, '__init__', lambda x: None):
            with mock.patch('git.Repo') as repo_mock:
                with mock.patch.object(CheckoutManager, 'is_git_dir', return_value=False):
                    CheckoutManager._get_repo(git_url, workspace)
                    repo_mock.clone_from.assert_called_once()

    def test_get_repo_not_existing(self):
        git_url = ''
        workspace = mock.MagicMock()
        workspace.path = mock.MagicMock()
        workspace.path.return_value = '/tmp/90209vsji'
        with mock.patch.object(git.Repo, '__init__', lambda x: None):
            with mock.patch('git.Repo') as repo_mock:
                with mock.patch.object(CheckoutManager, 'is_git_dir', return_value=True):
                    CheckoutManager._get_repo(git_url, workspace)
                    repo_mock.assert_called_once()

    def test_sync_repo(self):
        mock_repo = mock.MagicMock()
        CheckoutManager._sync_repo(mock_repo)
        mock_repo.git.remote.assert_called_once_with('update')
        mock_repo.git.reset.assert_called_once_with('--hard')
        mock_repo.git.clean.assert_called_once_with('-x', '-f', '-d', '-q')

    def test_checkout_ref(self):
        repo = mock.MagicMock()
        git_ref = 'test_git_ref'
        CheckoutManager._checkout_ref(repo, git_ref)
        repo.remotes.origin.fetch.assert_called_once_with(refspec=git_ref)
        repo.git.checkout.assert_called_once_with('FETCH_HEAD')
        repo.git.reset.assert_called_once_with('--hard', 'FETCH_HEAD')

    def test_init_submodules(self):
        workspace = mock.MagicMock()
        repo = mock.MagicMock()
        with mock.patch('os.path.isfile') as isfile_mock:
            isfile_mock.return_value = True
            CheckoutManager._init_submodules(workspace, repo)
            repo.git.submodules.assert_called()
            call_count = repo.git.submodules.call_count
            self.assertEquals(call_count, 3)
