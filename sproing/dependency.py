import typing
import container
from typing import Callable, Type

from sproing.container import get_return_type


class SproingDependency:

    def __init__(self, provider: Callable):
        self.provider = provider

    def __call__(self):
        return self.provider()

    def return_type(self) -> Type[typing.Any]:
        return get_return_type(self.provider)


def dependency(fn: Callable) -> Callable:
    container.register_dependency(fn)
    return fn
