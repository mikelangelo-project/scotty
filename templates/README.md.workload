My workload generator
=====================

Directory structure
-------------------

| Path              | Description |
| ----------------- | ----------- |
| ./samples         | Includes samples like experiment.yaml |
| ./workload_gen.py | Entry module if scotty runs a experiment with this workload |

Getting Started
---------------

Implement the workload generator like a python module. Your code should implemented under a subdirectory.    
Three interfaces must be implemented from workload_gen.py:

| Methode         | Description |
| --------------- | ----------- |
| result(context) | Is called from scotty until result gices an result != nil <br> Check the state of your workload here and return false if the workload has no results yet otherwise return true (You must save the results yourself) |
| run(context)    | Is called from scotty if the workload is started. Please implement this methode as a non blocking methode and collect state and results in the result methode |
| clean(context)  | Is called from scotty if the workload is finished. Clean all workload related stuff here |

You can test your workload implementation by starting the sample experiment under ./samples/experiment.yaml

    scotty experiment perform -c ./samples/experiment.yaml

After this run you find your results under the directory ./.scotty. You clean it by calling:

    scotty experiment clean 

Experiment Yaml
---------------

A workload generator can only be executed by an experiment. An experiment is defined by a experiment.yaml.

experiment.yaml:

    description: my experiment with my workload
    tags:
      - my_tag
    workloads:
      - name: myworkload
        generator: file:.
        params:
          greeting: Hallo

You can define a description and a list of tags for the experiment. Inside the section workloads you can define a list of workloads. The name is your choice but must be unique.    
The generator must be an existing directory relative to the experiment workspace (where you run 'scotty experiment perform') or a public git repository. Samples:

Existing workload generator in a directory where you run 'scotty experiment perform':

    generator: file:.

Existing workload generator in a public git repository:

    generator: git:git@gitolite.gwdg.de:scotty/workload/demo:master

The params section is free for use. So you can add a list of self-defined paramters. This parameters can called by the context from your workload_generator. Samples:

experiment.yaml section workloads

    ...
    params:
      greeting: Hallo
    ...
    
Implementation in the workload module

    def run(context):
      workload = context.v1.workload
      greeting = workload.params['greeting']
