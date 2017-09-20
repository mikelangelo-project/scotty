My resource generator
=====================

Directory structure
-------------------

| Path              | Description |
| ----------------- | ----------- |
| ./samples         | Includes samples like experiment.yaml |
| ./resource_gen.py | Entry module if scotty runs a experiment with this resource |

Getting Started
---------------

Implement the resource generator like a python module. Your code should implemented under a subdirectory.    
Three interfaces must be implemented from resource_gen.py

| Method            | Description |
| ----------------- | ----------- |
| endpoint(context) | Is called from scotty until endpoint gives an result != nil <br> Check the state of your resource here and return nil if the workload has no endpoint yet otherwise return dict with the endpoint data |
| deploy(context)   | Is called from scotty if the resource will be deployed. Please implement this methode as a non blocking methode and collect the state and endpoint in the endpoint methode |
| clean(context)    | Is called from scotty if the resource will be cleaned |

You can test your resource implementation by starting the sample experiment under ./samples/experiment.yaml.

    scotty experiment perform -c ./samples/experiment.yaml

After this run you find your scotty data under the directory ./.scotty. You can clean it by calling:

    scotty experiment clean

Experiment Yaml
---------------

A resource generator can only be executed by an experiment. An experiment is defined by a experiment.yaml.

experiment.yaml:

    description: my experiment with my resource
    tags:
      - my_tag
    resources:
      - name: my_resource_def
        generator: file:.
        params:
          user: myuser
          passwd: <%= ENV['mysecret'] %>

You can define a description and a list of tags for the experiment. Inside the section resources you can define a list of resources for the experiment. The name is in your choice but must be unique. For the generator you can use two types of repositories (git and file). In case of file you must write file:<relative path to the exoeriment workspace> (experiment workspace: where you run 'scotty experiment perform'). In case of git you must write git:<public git repository. Samples:

Existing resource generator in a directory where you run 'scotty experiment perform':

    generator: file:.

Existing resource generator in a public git repository:

    generator: git:git@gitolite.gwdg.de:scotty/resource/demo:master

The params section is free for use. So you can add a list of self-defined paramters. This parameters can called by the context from your resource generator. Samples:

experiment.yaml section resources

    ...
    params:
      greeting: Hallo
    ...
    
Implementation in the resource module

    def deploy(context):
      resource = context.v1.resource
      greeting = resource.params['greeting']
