class CommandRegistry(object):
    registry = {}
 
    @classmethod
    def addparser(cls, parser):
        module_ = parser.__module__
        key     = cls.getcommandkey(module_)
        cls.registry[key] = cls.registry.get(key, {})
        cls.registry[key]['parser'] = parser 
        return parser

    @classmethod
    def addbuilder(cls, builder):
        module_ = builder.__module__
        key     = cls.getcommandkey(module_)
        cls.registry[key] = cls.registry.get(key, {})
        cls.registry[key]['builder'] = builder
        return builder

    @classmethod
    def getcommandkey(cls, module_):
        key = module_.rsplit('.', 1)[-1]
        return key
 
    @classmethod
    def getbuilder(cls, command):
        builder = cls.registry[command]['builder']
        return builder()

    @classmethod
    def getparser(cls, command):
        parser = cls.registry[command]['parser']
        return parser()

class CommandParser(object):
    def add_arguments(self, parser):
        raise NotImplementedError(
            'You must implement CommandParser.add_arguments(self, parser)')
        
class CommandBuilder(object):
    command_class = None
    def buildCommand(self, options):
        if not self.command_class:
            raise NotImplementedError(
                'You must implement CommandBuilder.command_class')
        command = self.command_class(options)
        return command
