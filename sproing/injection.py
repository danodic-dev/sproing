from typing import Callable, Dict, get_type_hints, Any

import container


def __get_injected_dependencies(fn: Callable) -> Dict[str, Any]:
    argspec = get_type_hints(fn)
    dependencies = {}
    for argname, hint in argspec.items():
        dependency = container.get_dependency(hint)
        dependencies[argname] = dependency()
    return dependencies


def inject(fn: Callable) -> Callable:
    def injected():
        dependencies = __get_injected_dependencies(fn)
        return fn(**dependencies)

    return injected()
