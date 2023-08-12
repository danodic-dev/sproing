from typing import get_type_hints, Callable, Dict, Any

from sproing.container import get_dependency


def __get_injected_dependencies(fn: Callable) -> Dict[str, Any]:
    argspec = get_type_hints(fn)
    dependencies = {}
    for argname, hint in argspec.items():
        dependencies[argname] = get_dependency(hint)
    return dependencies


def inject(fn: Callable) -> Callable:
    def injected():
        dependencies = __get_injected_dependencies(fn)
        return fn(**dependencies)

    return injected()
