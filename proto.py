from collections import deque
from dataclasses import dataclass
from inspect import getargspec, signature, Parameter
from types import MappingProxyType
from typing import Callable, Type, get_type_hints, Dict, Any, List

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


@dataclass
class ArgumentError:
    argument_name: str
    dependency_name: str
    error_message: str


@dataclass
class ReturnError:
    dependency_name: str
    error_message: str


def validate_dependencies(fn: Callable) -> List[ArgumentError | ReturnError]:
    def is_valid_argument(argument: Parameter,
                          hints: Dict[str, Any]):
        return argument.name in hints

    def validate_arguments(arguments: MappingProxyType[str, Parameter],
                           hints: Dict[str, Any]):
        validations = {}
        for argument in arguments.values():
            validations[argument.name] = is_valid_argument(argument, hints)
        return validations

    def argument_validation_error(arg_name: str,
                                  dep_name: str) -> ArgumentError:
        return ArgumentError(argument_name=arg_name,
                             dependency_name=dep_name,
                             error_message=f"Dependency '{dep_name}' does not have a type hint for the argument '{arg_name}'.")

    def return_validation_error(dep_name: str) -> ReturnError:
        return ReturnError(dependency_name=dep_name,
                           error_message=f"Dependency '{dep_name}' does not have a type hint for its return type.")

    def has_valid_return(hints: Dict[str, Any]):
        return 'return' in hints

    hints = get_type_hints(fn)
    sign = signature(fn)

    dependency_name = fn.__name__
    validation_errors = []
    validation = validate_arguments(sign.parameters, hints)
    if not all(validation.values()):
        for arg, result in validation:
            if not result:
                error = argument_validation_error(arg, dependency_name)
                validation_errors.append(error)

    if not has_valid_return(hints):
        validation_errors.append(return_validation_error(dependency_name))

    return validation_errors


def dependency(fn: Callable):
    if errors := validate_dependencies(fn):
        raise RuntimeError(str(errors))
    hints = get_type_hints(fn)
    register_dependency(hints['return'], fn)
    return fn


def dep_lookup(dep_type: Type) -> Dependency:
    return dependencies[dep_type][0]


def inject(fn: Callable):
    def wrapper():
        kwargs = get_type_hints(fn)
        if 'return' in kwargs:
            del kwargs['return']
        kwargs = {key: dep_lookup(value)() for key, value in kwargs.items()}
        return fn(**kwargs)

    return wrapper
