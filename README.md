Scotty
======

Download and Install 
--------------------

Clone from repository and run pip install -r requirements.txt. Scotty run with **Python 2.7**. 
    
Add scotty to /usr/bin    

    ln -s /path/to/scotty/scotty.py /usr/bin/scotty

Perform a experiment
--------------------
    
    cd /path/to/experiment
    scotty experiment perform

Run the tests
-------------

    pytest
    
Rebase changed master into your feature/<branch>
-------------

    git checkout feature/<branch>
    git fetch
    git rebase origin/master
    git push

Install Gitlab Runner 
--------------------

https://docs.gitlab.com/runner/install/linux-repository.html

    curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-ci-multi-runner/script.deb.sh | sudo bash

    cat > /etc/apt/preferences.d/pin-gitlab-runner.pref <<EOF
    Explanation: Prefer GitLab provided packages over the Debian native ones
    Package: gitlab-ci-multi-runner
    Pin: origin packages.gitlab.com
    Pin-Priority: 1001
    EOF

    sudo apt-get install gitlab-ci-multi-runner

    # User Token from the project and tag "scotty-agent"
    sudo gitlab-ci-multi-runner register
    
    # Edit etc/gitlab-runner/config.toml
    concurrent = 1
    check_interval = 0

    [[runners]]
    name = "scotty-agent"
    url = "https://gitlab.gwdg.de/"
    token = "1f956c523c370bbf27a548b1d5795a"
    executor = "shell"
    limit = 1
    [runners.cache]
    
    gitlab-runner restart
    gitlab-runner verify
