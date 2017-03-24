class CommandRegistry(object):
    registry = {}

    @classmethod
    def addparser(cls, parser_class):
        module_ = parser_class.__module__
        key = cls.getcommandkey(module_)
        cls.registry[key] = cls.registry.get(key, {})
        cls.registry[key]['parser'] = parser_class
        return parser_class

    @classmethod
    def addbuilder(cls, builder_class):
        module_ = builder_class.__module__
        key = cls.getcommandkey(module_)
        cls.registry[key] = cls.registry.get(key, {})
        cls.registry[key]['builder'] = builder_class
        return builder_class

    @classmethod
    def getcommandkey(cls, module_):
        key = module_.rsplit('.', 1)[-1]
        return key

    @classmethod
    def getbuilder(cls, command):
        builder_class = cls.registry[command]['builder']
        return builder_class()

    @classmethod
    def getparser(cls, command):
        parser_class = cls.registry[command]['parser']
        return parser_class()


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
