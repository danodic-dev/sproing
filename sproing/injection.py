from . import container as c
import typing as t


def __get_injected_dependencies(fn: t.Callable) -> t.Dict[str, t.Any]:
    argspec = t.get_type_hints(fn)
    dependencies = {}
    for argname, hint in argspec.items():
        dependency = c.get_dependency(hint)
        dependencies[argname] = dependency()
    return dependencies


def inject(fn: t.Callable) -> t.Callable:
    def injected():
        dependencies = __get_injected_dependencies(fn)
        return fn(**dependencies)

    return injected()
