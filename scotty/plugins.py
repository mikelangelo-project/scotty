import imp

class PluginLoader(object):
    @classmethod
    def load_by_path(cls, path, workload_conf):
        workload_gen = imp.load_source('scotty.workload_gen', path)
        context = {'workload_conf': {}}
        workload_gen.run(context)
