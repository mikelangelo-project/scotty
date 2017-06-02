Scotty
======

Run Legacy Experiment
---------------------

    source ./samples/experiment
    ./scotty.py legacy experiment -w /path/to/workspace

Run Legacy Workload-Generator
-----------------------------

Checkout from zuul and run workload:

    source ./samples/workload-generator
    ./scotty.py legacy workload_generator -w /path/to/workspace
    
Skip checkout and run existing workload from workspace:

    ./scotty.py legacy workload_generator -w /path/to/workspace -s

Run a Workload
--------------

    ./scotty.py workload run -w samples/workload

Run an Experiment
-----------------

    ./scotty.py experiment run -w samples/component/experiment/ -s


Run the Tests
-------------

    python -m unittest discover tests

    python-coverage run --source=. -m unittest discover -s tests/
    python-coverage report -m --omit=scotty/legacy/*,scotty/cmd/legacy.py

Run the Tests with pytest
-------------------------

    pytest
    
Rebase changed master into your feature/<branch>
-------------

    git checkout feature/<branch>
    git fetch
    git rebase origin/master
    git push
