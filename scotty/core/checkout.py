import logging
import os

import git
import shutil

from scotty.core.exceptions import ScottyException

logger = logging.getLogger(__name__)


class CheckoutManager(object):
    @classmethod
    def populate(cls, component, base_path):
        generator = component.generator
        if generator['type'] == "git":
            cls.checkout(generator['location'], component.workspace, generator['reference'])
        elif generator['type'] == "file":
            cls.copy(component, generator['location'], base_path)
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
        shutil.rmtree(component.workspace.path, True)
        ignore_scotty = shutil.ignore_patterns(".scotty")
        shutil.copytree(source_path_abs, component.workspace.path, ignore=ignore_scotty)

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
            print 'foo'
            repo.git.submodule('init')
            repo.git.submodule('sync')
            repo.git.submodule('update', '--init')
