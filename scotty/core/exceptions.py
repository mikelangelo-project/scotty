class ScottyException(Exception):
    pass


class ExperimentException(ScottyException):
    pass


class WorkloadException(ScottyException):
    pass


class ResourceException(ScottyException):
    pass
