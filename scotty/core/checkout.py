import logging
import os

import git

logger = logging.getLogger(__name__)

class Manager(object):
    def checkout(self, workspace, project, origin_url, update_url, ref):
        url = '{url}{project}'.format(url=origin_url, project=project)
        repo = self._create_repo(workspace, url)
        self._clean_repo(repo, True)
        if not update_url:
            update_url = origin_url
        url = '{url}{project}'.format(url=update_url, project=project)
        self._update_repo(repo, url, ref)
        self._clean_repo(repo)
        self._init_submodules(workspace, repo)

    def _create_repo(self, workspace, url):
        repo = git.cmd.Git(workspace.path)
        if not os.path.isdir('{path}/.git'.format(path=workspace.path)):
            repo.clone(url, '.')
        return repo

    def _clean_repo(self, repo, reset=False):
        if reset:
            repo.remote('update')
            repo.reset('--hard')
        repo.clean('-x', '-f', '-d', '-q')

    def _update_repo(self, repo, url, ref):
        if ref.startswith('refs/tags'):
            raise scotty.core.exceptions.ScottyException('Checkout of refs/tags not supported')
        else:
            repo.fetch(url, ref)
            repo.checkout('FETCH_HEAD')
            repo.reset('--hard', 'FETCH_HEAD')

    def _init_submodules(self, workspace, repo):
        if os.path.isfile('{path}/.gitmodules'.format(path=workspace.path)):
            repo.submodules('init')
            repo.submodules('sync')
            repo.submodules('update', '--init')
