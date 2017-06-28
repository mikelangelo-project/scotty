import logging
import os

import git
import distutils.dir_util as dir_util

from scotty.core.exceptions import ScottyException

logger = logging.getLogger(__name__)


class CheckoutManager(object):
    @classmethod
    def populate(cls, component, base_path):
        source = component.config['generator'].split(':')
        source = dict(enumerate(source, 0))
        if component.issource('git'):
            git_url = "{}:{}".format(source[1], source[2])
            git_ref = source.get(3, None)
            cls.checkout(git_url, component.workspace, git_ref)
        elif component.issource('file'):
            cls.copy(component, source[1], base_path)
        else:
            raise ScottyException('Unsupported source type, Use "git" or "file"')

    @classmethod
    def copy(cls, component, source_path, base_path):
        if os.path.isabs(source_path):
            error_message = 'Source ({}) for component ({}) must be relative'.format(
                source_path,
                component.name)
            logger.error(error_message)
            raise ScottyException(error_message)
        source_path_abs = os.path.join(base_path, source_path, '.')
        dir_util.copy_tree(source_path_abs, component.workspace.path)

    @classmethod
    def checkout(cls, git_url, workspace, git_ref=None):
        repo = cls._get_repo(git_url, workspace)
        cls._sync_repo(repo)
        cls._checkout_ref(repo, git_ref)
        cls._init_submodules(workspace, repo)

    @classmethod
    def is_git_dir(cls, path):
        return os.path.isdir('{path}/.git'.format(path=path))

    @classmethod
    def _get_repo(cls, git_url, workspace):
        if not cls.is_git_dir(workspace.path):
            repo = git.Repo.clone_from(git_url, workspace.path)
        else:
            repo = git.Repo(workspace.path)
        return repo

    @classmethod
    def _sync_repo(cls, repo):
        repo.git.remote('update')
        repo.git.reset('--hard')
        repo.git.clean('-x', '-f', '-d', '-q')

    @classmethod
    def _checkout_ref(cls, repo, git_ref):
        if git_ref is not None:
            repo.remotes.origin.fetch(refspec=git_ref)
            repo.git.checkout('FETCH_HEAD')
            repo.git.reset('--hard', 'FETCH_HEAD')

    @classmethod
    def _init_submodules(cls, workspace, repo):
        if os.path.isfile('{path}/.gitmodules'.format(path=workspace.path)):
            repo.git.submodules('init')
            repo.git.submodules('sync')
            repo.git.submodules('update', '--init')
