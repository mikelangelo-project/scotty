from collections import defaultdict


class CommandRegistry(object):
    registry = defaultdict(dict)

    @classmethod
    def parser(cls, parser_class):
        module_ = parser_class.__module__
        key = cls.getcommandkey(module_)
        cls.registry[key]['parser'] = parser_class
        return parser_class

    @classmethod
    def command(cls, command_class):
        module_ = command_class.__module__
        key = cls.getcommandkey(module_)
        cls.registry[key]['command'] = command_class
        return command_class

    @classmethod
    def getcommandkey(cls, module_):
        key = module_.rsplit('.', 1)[-1]
        return key

    @classmethod
    def getbuilder(cls, command):
        builder_class = cls.registry[command].get('builder', CommandBuilder)
        return builder_class()

    @classmethod
    def getparser(cls, command):
        parser_class = cls.registry[command].get('parser', CommandParser)
        return parser_class()

    @classmethod
    def getcommand_class(cls, command):
        return cls.registry[command]['command']


class CommandParser(object):
    def add_arguments(self, parser):
        raise NotImplementedError(
            'You must implement CommandParser.add_arguments(self, parser)')


class CommandBuilder(object):
    def buildCommand(self, options, command_class):
        command = command_class(options)
        return command
