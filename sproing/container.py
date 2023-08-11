from typing import Callable, Dict, Type, get_type_hints, Any, List

from sproing.dependency import SproingDependency

DEPENDENCIES_TYPE = Dict[Type, List[SproingDependency]]

dependencies: DEPENDENCIES_TYPE = {}


def get_return_type(fn_: Callable):
    return get_type_hints(fn_)['return']


def register_dependency(fn: Callable) -> DEPENDENCIES_TYPE:
    dependency = SproingDependency(fn)
    dependencies.setdefault(dependency.return_type(), []).append(dependency)
    return dependencies


class NoSuchSproingDependency(Exception):
    def __init__(self, dependency_type: Type):
        super().__init__(f"No dependency registered for type: {str(dependency_type)}")
        self.dependency_type = dependency_type


def get_dependency(dependency_type: Type = None) -> SproingDependency:
    if dependency_type not in dependencies:
        raise NoSuchSproingDependency(dependency_type)
    return dependencies[dependency_type][0]
