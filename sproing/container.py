from __future__ import annotations

from typing import Type, Callable, get_type_hints, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from sproing.dependency import SproingDependency

PRIMARIES_TYPE = Dict[type, "SproingDependency"]
DEPENDENCIES_TYPE = Dict[Type, List["SproingDependency"]]
NAMED_DEPENDENCIES_TYPE = Dict[str, "SproingDependency"]

primaries: PRIMARIES_TYPE
dependencies: DEPENDENCIES_TYPE
named_dependencies: NAMED_DEPENDENCIES_TYPE


def initialize_container():
    global primaries, dependencies, named_dependencies
    primaries = {}
    dependencies = {}
    named_dependencies = {}


initialize_container()


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


class SproingNamedDependencyError(Exception):
    def __init__(self, dependency_name: str, name: str):
        super().__init__(
            f"Error registering dependency '{dependency_name}'. "
            f"Another dependency is already using the name: {name}")


class SproingDependencyError(Exception):
    def __init__(self, error: str):
        super().__init__(error)


def __register_named_dependency(dependency: "SproingDependency", name: str):
    if name in named_dependencies:
        raise SproingNamedDependencyError(dependency.name, name)
    named_dependencies[name] = dependency


def register_dependency(dependency: SproingDependency,
                        primary: bool,
                        name: str = None) -> DEPENDENCIES_TYPE:
    dependencies.setdefault(dependency.return_type(), []).append(dependency)

    if primary and name:
        raise SproingDependencyError(f"Error registering dependency '{dependency.name}'. "
                                     "A dependency cannot be both primary and named.")
    elif primary:
        __register_primary_dependency(dependency)
    elif name:
        __register_named_dependency(dependency, name)
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


class NoSuchNamedSproingDependency(Exception):
    def __init__(self, name: str, dependency_type: Type):
        super().__init__(f"No dependency registered for name and type: {name}, {str(dependency_type)}")
        self.dependency_type = dependency_type


def get_named_dependency(dependency_name: str) -> "SproingDependency":
    if dependency_name not in named_dependencies:
        raise NoSuchNamedSproingDependency(dependency_name, type)
    return named_dependencies[dependency_name]
