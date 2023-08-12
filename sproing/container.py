from __future__ import annotations

from typing import Type, Callable, get_type_hints, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from sproing.dependency import SproingDependency

PRIMARIES_TYPE = Dict[type, "SproingDependency"]
DEPENDENCIES_TYPE = Dict[Type, List["SproingDependency"]]

primaries: PRIMARIES_TYPE = {}
dependencies: DEPENDENCIES_TYPE = {}


def get_return_type(fn_: Callable):
    return get_type_hints(fn_)['return']


class SproingPrimaryDependencyError(Exception):
    def __init__(self, dependency_name: str, type_hint: str):
        super().__init__(
            f"Dependency '{dependency_name}' is set as primary, but there is already "
            f"a primary dependency for the type: {type_hint}.")


def __register_primary_dependency(dependency: "SproingDependency"):
    if dependency.return_type() in primaries:
        raise SproingPrimaryDependencyError(dependency.name, str(dependency.return_type()))
    primaries[dependency.return_type()] = dependency


def register_dependency(dependency: SproingDependency, primary: bool) -> DEPENDENCIES_TYPE:
    dependencies.setdefault(dependency.return_type(), []).append(dependency)
    if primary:
        __register_primary_dependency(dependency)
    return dependencies


class NoSuchSproingDependency(Exception):
    def __init__(self, dependency_type: Type):
        super().__init__(f"No dependency registered for type: {str(dependency_type)}")
        self.dependency_type = dependency_type


def get_dependency(dependency_type: Type = None) -> "SproingDependency":
    if dependency_type in primaries:
        return primaries[dependency_type]
    elif dependency_type not in dependencies:
        raise NoSuchSproingDependency(dependency_type)
    return dependencies[dependency_type][0]
