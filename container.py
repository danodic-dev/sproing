from collections import deque
from inspect import getargspec, signature, Parameter
from types import MappingProxyType
from typing import Callable, Type, get_type_hints, Dict, Any

dependencies = {}


class Dependency:
    def __init__(self,
                 fn: Callable,
                 singleton: bool = False,
                 lazy: bool = True):
        self.fn = fn
        self.singleton = singleton
        self.instance = None

        self.strategy = self.__factory
        if singleton:
            self.strategy = self.__singleton

        if not lazy:
            self.singleton = self.__singleton()

    def __call__(self):
        return self.strategy()

    def __singleton(self):
        return self.singleton or self.__instantiate_singleton()

    def __instantiate_singleton(self):
        self.singleton = self.fn()
        return self.singleton

    def __factory(self):
        return self.fn()


def register_dependency(return_type: Type,
                        provider: Callable):
    if return_type not in dependencies:
        dependencies[return_type] = deque()
    dependencies[return_type].append(Dependency(provider))


def is_valid_dependency(fn: Callable) -> bool:
    def is_valid_argument(argument: Parameter,
                          hints: Dict[str, Any]):
        return argument.name in hints

    def validate_arguments(arguments: MappingProxyType[str, Parameter],
                           hints: Dict[str, Any]):
        validation = {}
        for argument in arguments.values():
            validation[argument.name] = is_valid_argument(argument, hints)
        return validation

    def has_valid_return(hints: Dict[str, Any]):
        return 'return' in hints

    hints = get_type_hints(fn)
    sign = signature(fn)

    validation = validate_arguments(sign.parameters, hints)
    #if not all([])



def dependency(fn: Callable):
    hints = get_type_hints(fn)
    register_dependency(hints['return'], fn)
    return fn


def dep_lookup(dep_type: typing.Type) -> Dependency:
    return dependencies[dep_type]


def inject(fn: Callable):
    def wrapper():
        kwargs = typing.get_type_hints(fn)
        if 'return' in kwargs:
            del kwargs['return']
        kwargs = {key: dep_lookup(value)() for key, value in kwargs.items()}
        return fn(**kwargs)

    return wrapper
