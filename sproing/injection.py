from typing import get_type_hints, Callable, Dict, Any, List

from sproing.container import get_dependency, get_named_dependency


class SproingInvalidExplicitArgumentName(Exception):
    def __init__(self, injected_name: str, argname: str):
        super().__init__(
            f"Injected callable '{injected_name}' explicitly defines the injection for argument {argname}, "
            f"but the callable does not declare this argument in its list of arguments.")


class SproingInjectionDefinitionError(Exception):
    def __init__(self, injection_name: str, errors: List[Exception]):
        super().__init__(self.__make_message(injection_name, errors))
        self.injection_name = injection_name
        self.errors = errors

    @staticmethod
    def __make_message(injection_name: str,
                       errors: List[Exception]):
        errors_str = "\n\t".join(str(error) for error in errors)
        return f"Bad definition of injection '{injection_name}':\n\t{errors_str}"


def __validate_explicit_names(injected_name: str, argspec, explicit: Dict[str, str]):
    errors = []
    for argname in explicit:
        if argname not in argspec:
            error = SproingInvalidExplicitArgumentName(injected_name, argname)
            errors.append(error)
    if errors:
        raise SproingInjectionDefinitionError(injected_name, errors)


def __get_explicit_injection(explicit: Dict[str, str]) -> Dict[str, Any]:
    dependencies = {}
    for argname, depname in explicit.items():
        dependencies[argname] = get_named_dependency(depname)()
    return dependencies


def __get_default_injection(fn: Callable, explicit: Dict[str, str]) -> Dict[str, Any]:
    argspec = get_type_hints(fn)
    dependencies = {}
    for argname, hint in argspec.items():
        if argname != 'return' and (not explicit or argname not in explicit):
            resolved = get_dependency(hint)
            if len(resolved) > 1:
                dependencies[argname] = [dependency() for dependency in resolved]
            else:
                nested_dependencies = __get_injected_dependencies(resolved[0].provider)
                dependencies[argname] = resolved[0](**nested_dependencies)
    return dependencies


def __get_injected_dependencies(fn: Callable, explicit: Dict[str, str] | None = None) -> Dict[str, Any]:
    argspec = get_type_hints(fn)
    dependencies = {}
    if explicit:
        __validate_explicit_names(fn.__name__, argspec, explicit)
        dependencies.update(__get_explicit_injection(explicit))
    dependencies.update(__get_default_injection(fn, explicit))
    return dependencies


def inject(*, explicit=None) -> Callable:
    def wrapper(fn: Callable) -> Callable:
        def injected(*_, **__) -> Callable:
            dependencies = __get_injected_dependencies(fn, explicit)
            return fn(**dependencies)

        return injected

    return wrapper
