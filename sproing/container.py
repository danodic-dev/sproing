from typing import Callable, Dict, Type, get_type_hints, Any, List

from sproing.dependency import SproingDependency

dependencies: Dict[Type, SproingDependency] = {}


def get_return_type(fn_: Callable):
    return get_type_hints(fn_)['return']


def register_dependency(fn: Callable) -> Dict[Any, SproingDependency]:
    dependency = SproingDependency(fn)
    dependencies[dependency.return_type()] = dependency
    return dependencies


class NoSuchSproingDependency(Exception):
    def __init__(self, dependency_type: Type):
        super().__init__(f"No dependency registered for type: {str(dependency_type)}")
        self.dependency_type = dependency_type


def get_dependency(dependency_type: Type = None) -> SproingDependency:
    if dependency_type not in dependencies:
        raise NoSuchSproingDependency(dependency_type)
    return dependencies[dependency_type]
