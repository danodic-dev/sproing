from . import container as c
import typing as t
import inspect as i


class SproingDependency:

    def __init__(self, provider: t.Callable):
        self.provider = provider
        self.name = provider.__name__

    def __call__(self):
        return self.provider()

    def return_type(self) -> t.Type[t.Any]:
        return c.get_return_type(self.provider)


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
    def __init__(self, dependency_name: str, errors: t.List[SproingArgValidationError | SproingReturnValidationError]):
        super().__init__(self.__make_message(dependency_name, errors))
        self.dependency_name = dependency_name
        self.errors = errors

    @staticmethod
    def __make_message(dependency_name: str,
                       errors: t.List[SproingArgValidationError | SproingReturnValidationError]):
        errors_str = "\n\t".join(str(error) for error in errors)
        return f"Bad definition of dependency {dependency_name}:\n\t{errors_str}"


def __validate_parameters(dependency_name: str,
                          hints: t.Dict[str, t.Type],
                          parameters: t.Iterable[str]) -> t.List[SproingArgValidationError]:
    errors = []
    for parameter in parameters:
        if parameter not in hints:
            error = SproingArgValidationError(parameter, dependency_name, "No type hint provided.")
            errors.append(error)
    return errors


def __validate_return_type(dependency_name: str, hints: t.Dict[str, t.Type]) -> SproingReturnValidationError:
    if 'return' not in hints:
        error = SproingReturnValidationError(dependency_name, "No return type hint provided.")
        return error


def __validate_dependency(fn: t.Callable) -> t.List[SproingArgValidationError | SproingReturnValidationError]:
    hints = t.get_type_hints(fn)
    parameters = i.signature(fn).parameters

    errors = []
    errors.extend(__validate_parameters(fn.__name__, hints, parameters.keys()))
    if error := __validate_return_type(fn.__name__, hints):
        errors.append(error)

    return errors


def dependency(fn: t.Callable) -> t.Callable:
    if validation_errors := __validate_dependency(fn):
        raise SproingDependencyDefinitionError(fn.__name__, validation_errors)
    c.register_dependency(fn, primary=False)
    return fn
