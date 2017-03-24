import imp

class WorkloadLoader(object):
    @classmethod
    def load_by_path(cls, path,  name='anonymous_workload'):
        module_name = 'scotty.workload_gen.{name}'.format(name=name)
        workload = imp.load_source(module_name, path)
        return workload

