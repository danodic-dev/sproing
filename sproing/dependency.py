from __future__ import annotations

from inspect import signature
from typing import get_type_hints, Callable, List, Dict, Type, Iterable, Any

from sproing.container import register_dependency, get_return_type


class SproingDependency:

    def __init__(self, provider: Callable, *, singleton: bool = False, lazy: bool | None = None):
        self.provider = provider
        self.name = provider.__name__

        if not singleton and lazy is not None and not lazy:
            raise SproingLazyDependencyDefinitionError(self.name, "must be lazy when not singleton.")

        self.value = None
        self.strategy = self.__factory_strategy
        if singleton:
            self.strategy = self.__singleton_strategy
            if lazy is not None and not lazy:
                self.__initialize_singleton()

    def __call__(self, **kwargs):
        return self.strategy(**kwargs)

    def __singleton_strategy(self, **kwargs):
        return self.value or self.__initialize_singleton(**kwargs)

    def __initialize_singleton(self, **kwargs) -> Any:
        self.value = self.provider(**kwargs)
        return self.value

    def __factory_strategy(self, **kwargs) -> Any:
        return self.provider(**kwargs)

    def return_type(self) -> Type[Any]:
        return get_return_type(self.provider)


class SproingArgValidationError(Exception):
    def __init__(self, arg_name: str, dependency_name: str, error: str):
        super().__init__(f"Error validating argument '{arg_name}' for dependency '{dependency_name}': {error}")
        self.arg_name = arg_name
        self.dependency_name = dependency_name
        self.error = error


class SproingReturnValidationError(Exception):
    def __init__(self, dependency_name: str, error: str):
        super().__init__(f"Error validating return type for dependency '{dependency_name}': {error}")
        self.dependency_name = dependency_name
        self.error = error


class SproingDependencyDefinitionError(Exception):
    def __init__(self, dependency_name: str, errors: List[SproingArgValidationError | SproingReturnValidationError]):
        super().__init__(self.__make_message(dependency_name, errors))
        self.dependency_name = dependency_name
        self.errors = errors

    @staticmethod
    def __make_message(dependency_name: str,
                       errors: List[SproingArgValidationError | SproingReturnValidationError]):
        errors_str = "\n\t".join(str(error) for error in errors)
        return f"Bad definition of dependency {dependency_name}:\n\t{errors_str}"


class SproingLazyDependencyDefinitionError(Exception):
    def __init__(self, dependency_name: str, error: str):
        super().__init__(f"Error defining dependency '{dependency_name}' lazyness: {error}")
        self.dependency_name = dependency_name
        self.error = error


def __validate_parameters(dependency_name: str,
                          hints: Dict[str, Type],
                          parameters: Iterable[str]) -> List[SproingArgValidationError]:
    errors = []
    for parameter in parameters:
        if parameter not in hints:
            error = SproingArgValidationError(parameter, dependency_name, "No type hint provided.")
            errors.append(error)
    return errors


def __validate_return_type(dependency_name: str, hints: Dict[str, Type]) -> SproingReturnValidationError:
    if 'return' not in hints:
        error = SproingReturnValidationError(dependency_name, "No return type hint provided.")
        return error


def __validate_dependency(fn: Callable) -> List[SproingArgValidationError | SproingReturnValidationError]:
    hints = get_type_hints(fn)
    parameters = signature(fn).parameters

    errors = []
    errors.extend(__validate_parameters(fn.__name__, hints, parameters.keys()))
    if error := __validate_return_type(fn.__name__, hints):
        errors.append(error)

    return errors


def dependency(fn: Callable, *,
               primary: bool = False,
               name: str | None = None,
               singleton: bool = False,
               lazy: bool | None = None) -> SproingDependency:
    if validation_errors := __validate_dependency(fn):
        raise SproingDependencyDefinitionError(fn.__name__, validation_errors)
    sproing_dependency = SproingDependency(fn, singleton=singleton, lazy=lazy)
    register_dependency(sproing_dependency, primary, name)
    return sproing_dependency
